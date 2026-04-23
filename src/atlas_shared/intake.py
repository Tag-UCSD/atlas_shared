from __future__ import annotations

from dataclasses import asdict, dataclass, field
from importlib import resources
import json
import re
from typing import Any, Literal, Mapping, Sequence

from ._util import _split_terms
from .article_types import ArticleTypeDecision, HeuristicArticleTypeClassifier
from .bundle_router import BundleRoutingResult, QuestionBundleRouter
from .registry_sink import RegistryFact
from .relevance import (
    ArticleCandidate,
    QuestionArticleRelevanceFilter,
    QuestionConstitution,
    SupportsArticleTypeClassification,
    SupportsRelevanceAdjudication,
)


IntakeDecision = Literal[
    "accept_candidate",
    "edge_case",
    "needs_abstract",
    "needs_pdf_text",
    "manual_review",
    "reject_clear_false_positive",
]
RoutingTarget = Literal["article_eater", "manual_review", "hold_for_metadata", "reject"]
DomainRelevance = Literal[
    "on_domain",
    "adjacent_or_novel",
    "insufficient_metadata",
    "clear_false_positive",
    "unknown",
]
ProcessingStage = Literal[
    "pre_extraction",
    "post_ocr",
    "post_extraction",
    "rebuild",
    "unknown",
]


def _load_domain_lexicon() -> dict[str, tuple[str, ...]]:
    package_root = resources.files("atlas_shared")
    text = (package_root / "data" / "domain_lexicon.json").read_text(encoding="utf-8")
    payload = json.loads(text)
    if not isinstance(payload, Mapping):
        raise ValueError("domain_lexicon.json must contain a JSON object")
    loaded: dict[str, tuple[str, ...]] = {}
    for key in ("domain_signal_terms", "clear_false_positive_terms", "soft_false_positive_terms"):
        value = payload.get(key, ())
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            loaded[key] = tuple(str(item).strip() for item in value if str(item).strip())
        else:
            loaded[key] = ()
    return loaded


_DOMAIN_LEXICON = _load_domain_lexicon()
DOMAIN_SIGNAL_TERMS: tuple[str, ...] = _DOMAIN_LEXICON["domain_signal_terms"]
CLEAR_FALSE_POSITIVE_TERMS: tuple[str, ...] = _DOMAIN_LEXICON["clear_false_positive_terms"]
SOFT_FALSE_POSITIVE_TERMS: tuple[str, ...] = _DOMAIN_LEXICON["soft_false_positive_terms"]
def _norm_text(*pieces: str) -> str:
    return "\n".join(piece for piece in pieces if piece).lower()


def _summary_to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        sections = value.get("sections")
        if isinstance(sections, Mapping):
            return "\n".join(str(item or "") for item in sections.values())
        return " ".join(str(item or "") for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return " ".join(str(item or "") for item in value)
    return ""


def _has_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    pattern = re.escape(phrase.lower()).replace(r"\ ", r"[\s\-]+")
    return bool(re.search(rf"\b{pattern}\b", text, re.IGNORECASE))


def _hits(text: str, terms: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    found: list[str] = []
    for term in terms:
        cleaned = term.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        if _has_phrase(text, cleaned):
            found.append(cleaned)
            seen.add(cleaned)
    return tuple(found)


def _confidence_from_routing(routing: BundleRoutingResult | None, default: float = 0.45) -> float:
    if routing is None or not routing.candidates:
        return default
    return min(max(routing.candidates[0].best_confidence, default), 0.96)


def _derive_topic_label(article: "PreExtractionArticleIntake", domain_hits: Sequence[str]) -> str:
    if article.keywords:
        return str(article.keywords[0])
    if domain_hits:
        return " / ".join(domain_hits[:2]).title()
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", article.title)
    return " ".join(words[:8])


@dataclass(frozen=True)
class PreExtractionArticleIntake:
    """
    Metadata available when a PDF first arrives.

    This deliberately excludes Article Eater extraction outputs. First-page text
    is allowed because Article Finder can derive it before full V7 extraction.
    """

    paper_id: str
    title: str = ""
    abstract: str = ""
    filename: str = ""
    doi: str = ""
    zotero_tags: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    first_page_text: str = ""
    article_type: str = ""
    source: str = ""
    pdf_sha256: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    processing_stage: ProcessingStage = "pre_extraction"
    methods_surface_summary: str = ""
    science_writer_summary: str = ""
    independent_variables: tuple[str, ...] = ()
    dependent_variables: tuple[str, ...] = ()
    measurement_terms: tuple[str, ...] = ()
    instrument_terms: tuple[str, ...] = ()
    sensor_terms: tuple[str, ...] = ()
    topic_hints: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "PreExtractionArticleIntake":
        raw_measurement_inventory = obj.get("measurement_inventory")
        measurement_inventory = (
            raw_measurement_inventory
            if isinstance(raw_measurement_inventory, Sequence) and not isinstance(raw_measurement_inventory, (str, bytes))
            else ()
        )
        measurement_terms: list[str] = []
        instrument_terms: list[str] = []
        sensor_terms: list[str] = []
        for item in measurement_inventory:
            if not isinstance(item, Mapping):
                continue
            for key, target in (
                ("measure_name", measurement_terms),
                ("outcome", measurement_terms),
                ("instrument_name", instrument_terms),
                ("instrument_type", instrument_terms),
                ("sensor_name", sensor_terms),
                ("sensor_type", sensor_terms),
            ):
                value = str(item.get(key) or "").strip()
                if value:
                    target.append(value)
        return cls(
            paper_id=str(obj.get("paper_id") or obj.get("id") or obj.get("pdf_id") or ""),
            title=str(obj.get("title") or ""),
            abstract=str(obj.get("abstract") or ""),
            filename=str(obj.get("filename") or obj.get("file_name") or ""),
            doi=str(obj.get("doi") or ""),
            zotero_tags=_split_terms(obj.get("zotero_tags") or obj.get("tags")),
            keywords=_split_terms(obj.get("keywords")),
            first_page_text=str(obj.get("first_page_text") or obj.get("page_1_text") or ""),
            article_type=str(obj.get("article_type") or ""),
            source=str(obj.get("source") or ""),
            pdf_sha256=str(obj.get("pdf_sha256") or obj.get("sha256") or ""),
            metadata=dict(obj.get("metadata") or {}),
            processing_stage=str(obj.get("processing_stage") or obj.get("pipeline_stage") or "pre_extraction"),  # type: ignore[arg-type]
            methods_surface_summary=str(obj.get("methods_surface_summary") or ""),
            science_writer_summary=_summary_to_text(obj.get("science_writer_summary")),
            independent_variables=_split_terms(obj.get("independent_variables") or obj.get("iv_raw") or obj.get("iv_mapped")),
            dependent_variables=_split_terms(obj.get("dependent_variables") or obj.get("dv_raw") or obj.get("dv_mapped")),
            measurement_terms=tuple(measurement_terms) or _split_terms(obj.get("measurement_terms")),
            instrument_terms=tuple(instrument_terms) or _split_terms(obj.get("instrument_terms")),
            sensor_terms=tuple(sensor_terms) or _split_terms(obj.get("sensor_terms")),
            topic_hints=_split_terms(obj.get("topic_hints") or obj.get("topics") or obj.get("topic_candidates")),
        )

    def to_article_candidate(self) -> ArticleCandidate:
        body_text = _norm_text(
            self.first_page_text,
            self.methods_surface_summary,
            self.science_writer_summary,
            " ".join(self.independent_variables),
            " ".join(self.dependent_variables),
            " ".join(self.measurement_terms),
            " ".join(self.instrument_terms),
            " ".join(self.sensor_terms),
            " ".join(self.topic_hints),
        )
        return ArticleCandidate(
            paper_id=self.paper_id,
            title=self.title,
            abstract=self.abstract,
            article_type=self.article_type,
            keywords=self.keywords,
            body_text=body_text,
        )

    @property
    def available_text(self) -> str:
        return _norm_text(
            self.title,
            self.abstract,
            self.filename,
            " ".join(self.keywords),
            " ".join(self.zotero_tags),
            self.first_page_text,
            self.methods_surface_summary,
            self.science_writer_summary,
            " ".join(self.independent_variables),
            " ".join(self.dependent_variables),
            " ".join(self.measurement_terms),
            " ".join(self.instrument_terms),
            " ".join(self.sensor_terms),
            " ".join(self.topic_hints),
        )

    @property
    def has_substantive_text(self) -> bool:
        return bool(self.available_text.strip())

    @property
    def has_downstream_extraction_text(self) -> bool:
        return any(
            (
                self.methods_surface_summary,
                self.science_writer_summary,
                self.independent_variables,
                self.dependent_variables,
                self.measurement_terms,
                self.instrument_terms,
                self.sensor_terms,
                self.topic_hints,
            )
        )

    @property
    def available_evidence_types(self) -> tuple[str, ...]:
        evidence: list[str] = []
        for key, value in (
            ("title", self.title),
            ("abstract", self.abstract),
            ("first_page_text", self.first_page_text),
            ("methods_surface_summary", self.methods_surface_summary),
            ("science_writer_summary", self.science_writer_summary),
            ("independent_variables", self.independent_variables),
            ("dependent_variables", self.dependent_variables),
            ("measurement_terms", self.measurement_terms),
            ("instrument_terms", self.instrument_terms),
            ("sensor_terms", self.sensor_terms),
            ("topic_hints", self.topic_hints),
        ):
            if value:
                evidence.append(key)
        return tuple(evidence)


@dataclass(frozen=True)
class PreExtractionIntakeResult:
    paper_id: str
    intake_decision: IntakeDecision
    routing_target: RoutingTarget
    domain_relevance: DomainRelevance
    article_type: ArticleTypeDecision
    confidence: float
    needs_manual_review: bool
    reasons: tuple[str, ...] = ()
    primary_topic: str | None = None
    primary_bundle_id: str | None = None
    topic_candidates: tuple[str, ...] = ()
    matched_question_ids: tuple[str, ...] = ()
    edge_case_kind: str = "none"
    novelty_signal: float = 0.0
    topic_expansion_candidate: bool = False
    new_topic_candidate: bool = False
    proposed_topic_label: str = ""
    adjacent_topics: tuple[str, ...] = ()
    facts: tuple[RegistryFact, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["article_type"] = asdict(self.article_type)
        data["facts"] = [asdict(fact) for fact in self.facts]
        return data

    def to_classification_facts(self) -> tuple[RegistryFact, ...]:
        return self.facts


class PreExtractionIntakeGate:
    """
    Conservative first gate for newly arrived PDFs.

    The gate is intentionally hard to use as a blunt exclusion device. It sends
    plausible but unclassified novelty to review rather than rejecting it.
    """

    def __init__(
        self,
        constitutions: Sequence[QuestionConstitution] = (),
        *,
        classifier: SupportsArticleTypeClassification | None = None,
        adjudicator: SupportsRelevanceAdjudication | None = None,
        adjudication_policy: Literal["never", "borderline_only", "always"] = "borderline_only",
        lexicon_override: Mapping[str, Sequence[str]] | None = None,
    ) -> None:
        self.constitutions = tuple(constitutions)
        override = lexicon_override or {}
        self.domain_signal_terms = tuple(override.get("domain_signal_terms", DOMAIN_SIGNAL_TERMS))
        self.clear_false_positive_terms = tuple(
            override.get("clear_false_positive_terms", CLEAR_FALSE_POSITIVE_TERMS)
        )
        self.soft_false_positive_terms = tuple(
            override.get("soft_false_positive_terms", SOFT_FALSE_POSITIVE_TERMS)
        )
        self.filter = QuestionArticleRelevanceFilter(
            classifier=classifier or HeuristicArticleTypeClassifier(),
            adjudicator=adjudicator,
            adjudication_policy=adjudication_policy,
        )
        self.router = (
            QuestionBundleRouter(
                self.constitutions,
                classifier=classifier,
                adjudicator=adjudicator,
                adjudication_policy=adjudication_policy,
            )
            if self.constitutions
            else None
        )

    def assess(self, intake_like: PreExtractionArticleIntake | Mapping[str, Any]) -> PreExtractionIntakeResult:
        intake = (
            intake_like
            if isinstance(intake_like, PreExtractionArticleIntake)
            else PreExtractionArticleIntake.from_mapping(intake_like)
        )
        article = intake.to_article_candidate()
        article_type = self.filter.classify_article_type(article)
        text = intake.available_text
        domain_hits = _hits(text, self.domain_signal_terms)
        clear_false_positive_hits = _hits(text, self.clear_false_positive_terms)
        soft_false_positive_hits = _hits(text, self.soft_false_positive_terms)

        if not intake.has_substantive_text:
            return self._build_result(
                intake,
                article_type,
                decision="needs_abstract",
                routing_target="hold_for_metadata",
                domain_relevance="insufficient_metadata",
                confidence=0.20,
                needs_manual_review=True,
                reasons=("no title, abstract, keywords, tags, or first-page text available",),
            )

        if not intake.abstract and not intake.first_page_text and not intake.has_downstream_extraction_text:
            return self._build_result(
                intake,
                article_type,
                decision="needs_pdf_text",
                routing_target="hold_for_metadata",
                domain_relevance="insufficient_metadata",
                confidence=0.35,
                needs_manual_review=True,
                reasons=("title-level metadata is present, but abstract or first-page text is needed before exclusion",),
            )

        if clear_false_positive_hits:
            return self._build_result(
                intake,
                article_type,
                decision="reject_clear_false_positive",
                routing_target="reject",
                domain_relevance="clear_false_positive",
                confidence=0.92,
                needs_manual_review=False,
                reasons=(
                    "clear false-positive signals are present and no Atlas domain signals were found",
                    f"clear false-positive hits: {', '.join(clear_false_positive_hits)}",
                ),
            )

        if soft_false_positive_hits:
            return self._build_result(
                intake,
                article_type,
                decision="manual_review",
                routing_target="manual_review",
                domain_relevance="adjacent_or_novel" if domain_hits else "unknown",
                confidence=0.48,
                needs_manual_review=True,
                reasons=(
                    "soft false-positive signals are present and require manual review rather than hard rejection",
                    f"soft false-positive hits: {', '.join(soft_false_positive_hits)}",
                ),
            )

        routing = self.router.route_article(article) if self.router is not None else None
        accepted = tuple(
            item for item in (routing.all_assessments if routing else ()) if item.verdict == "accept"
        )
        edge_cases = tuple(
            item for item in (routing.all_assessments if routing else ()) if item.verdict == "edge_case"
        )
        emergent = routing.emergent_candidates if routing else ()
        topic_candidates = tuple(candidate.topic for candidate in routing.candidates) if routing else ()
        matched_question_ids = tuple(item.question_id for item in accepted + edge_cases)

        if accepted:
            return self._build_result(
                intake,
                article_type,
                decision="accept_candidate",
                routing_target="article_eater",
                domain_relevance="on_domain",
                confidence=_confidence_from_routing(routing, 0.82),
                needs_manual_review=False,
                reasons=("matched at least one existing question constitution",),
                routing=routing,
                topic_candidates=topic_candidates,
                matched_question_ids=matched_question_ids,
            )

        if edge_cases or emergent:
            best_edge = max(edge_cases, key=lambda item: item.confidence) if edge_cases else None
            topic_expansion_candidate = (
                any(item.topic_expansion_candidate for item in edge_cases)
                or bool(emergent)
                or bool(edge_cases)
            )
            new_topic_candidate = any(item.new_topic_candidate for item in edge_cases)
            proposed_topic_label = next(
                (
                    label
                    for item in edge_cases
                    for label in (item.proposed_topic_label,)
                    if label
                ),
                "",
            )
            if (topic_expansion_candidate or new_topic_candidate) and not proposed_topic_label:
                proposed_topic_label = _derive_topic_label(intake, domain_hits)
            return self._build_result(
                intake,
                article_type,
                decision="edge_case",
                routing_target="manual_review",
                domain_relevance="adjacent_or_novel",
                confidence=_confidence_from_routing(routing, 0.58),
                needs_manual_review=True,
                reasons=("preserved as adjacent, borderline, or emergent-topic evidence",),
                routing=routing,
                topic_candidates=topic_candidates,
                matched_question_ids=matched_question_ids,
                edge_case_kind=(
                    best_edge.edge_case_kind
                    if best_edge and best_edge.edge_case_kind != "undetermined"
                    else "topic_expansion_candidate"
                ),
                novelty_signal=max(
                    [item.novelty_signal for item in edge_cases]
                    + [candidate.max_novelty_signal for candidate in emergent]
                    + [0.65]
                ),
                topic_expansion_candidate=topic_expansion_candidate,
                new_topic_candidate=new_topic_candidate,
                proposed_topic_label=proposed_topic_label,
                adjacent_topics=tuple(
                    sorted({topic for item in edge_cases for topic in item.adjacent_topics})
                ),
            )

        if domain_hits:
            label = _derive_topic_label(intake, domain_hits)
            return self._build_result(
                intake,
                article_type,
                decision="edge_case",
                routing_target="manual_review",
                domain_relevance="adjacent_or_novel",
                confidence=0.56,
                needs_manual_review=True,
                reasons=(
                    "domain signals are present, but no existing topic constitution captured the article",
                    f"domain signal hits: {', '.join(domain_hits)}",
                ),
                topic_candidates=(label,),
                edge_case_kind="new_topic_candidate",
                novelty_signal=0.72,
                new_topic_candidate=True,
                proposed_topic_label=label,
            )

        return self._build_result(
            intake,
            article_type,
            decision="manual_review",
            routing_target="manual_review",
            domain_relevance="unknown",
            confidence=0.42,
            needs_manual_review=True,
            reasons=("metadata is insufficient for a safe reject and no existing topic captured the article",),
        )

    def _build_result(
        self,
        intake: PreExtractionArticleIntake,
        article_type: ArticleTypeDecision,
        *,
        decision: IntakeDecision,
        routing_target: RoutingTarget,
        domain_relevance: DomainRelevance,
        confidence: float,
        needs_manual_review: bool,
        reasons: Sequence[str],
        routing: BundleRoutingResult | None = None,
        topic_candidates: Sequence[str] = (),
        matched_question_ids: Sequence[str] = (),
        edge_case_kind: str = "none",
        novelty_signal: float = 0.0,
        topic_expansion_candidate: bool = False,
        new_topic_candidate: bool = False,
        proposed_topic_label: str = "",
        adjacent_topics: Sequence[str] = (),
    ) -> PreExtractionIntakeResult:
        primary_topic = routing.primary_topic if routing else None
        primary_bundle_id = routing.primary_bundle_id if routing else None
        if primary_topic and primary_topic not in topic_candidates:
            topic_candidates = (primary_topic, *tuple(topic_candidates))

        facts = self._facts(
            intake,
            article_type,
            decision=decision,
            routing_target=routing_target,
            domain_relevance=domain_relevance,
            confidence=confidence,
            reasons=tuple(reasons),
            primary_topic=primary_topic,
            primary_bundle_id=primary_bundle_id,
            topic_candidates=tuple(topic_candidates),
            matched_question_ids=tuple(matched_question_ids),
            edge_case_kind=edge_case_kind,
            novelty_signal=novelty_signal,
            topic_expansion_candidate=topic_expansion_candidate,
            new_topic_candidate=new_topic_candidate,
            proposed_topic_label=proposed_topic_label,
        )
        return PreExtractionIntakeResult(
            paper_id=intake.paper_id,
            intake_decision=decision,
            routing_target=routing_target,
            domain_relevance=domain_relevance,
            article_type=article_type,
            confidence=round(confidence, 4),
            needs_manual_review=needs_manual_review,
            reasons=tuple(reasons),
            primary_topic=primary_topic,
            primary_bundle_id=primary_bundle_id,
            topic_candidates=tuple(topic_candidates),
            matched_question_ids=tuple(matched_question_ids),
            edge_case_kind=edge_case_kind,
            novelty_signal=round(novelty_signal, 4),
            topic_expansion_candidate=topic_expansion_candidate,
            new_topic_candidate=new_topic_candidate,
            proposed_topic_label=proposed_topic_label,
            adjacent_topics=tuple(adjacent_topics),
            facts=facts,
        )

    def _facts(
        self,
        intake: PreExtractionArticleIntake,
        article_type: ArticleTypeDecision,
        *,
        decision: IntakeDecision,
        routing_target: RoutingTarget,
        domain_relevance: DomainRelevance,
        confidence: float,
        reasons: tuple[str, ...],
        primary_topic: str | None,
        primary_bundle_id: str | None,
        topic_candidates: tuple[str, ...],
        matched_question_ids: tuple[str, ...],
        edge_case_kind: str,
        novelty_signal: float,
        topic_expansion_candidate: bool,
        new_topic_candidate: bool,
        proposed_topic_label: str,
    ) -> tuple[RegistryFact, ...]:
        facts: list[RegistryFact] = [
            RegistryFact(
                dimension="article_type_preliminary",
                label=article_type.value,
                confidence=round(article_type.confidence, 4),
                schema_version="pre_extraction_intake_v1",
                paper_id=intake.paper_id,
                details_json={
                    "paper_id": intake.paper_id,
                    "source": article_type.source,
                    "evidence": list(article_type.evidence),
                    "processing_stage": intake.processing_stage,
                    "available_evidence_types": list(intake.available_evidence_types),
                },
            ),
            RegistryFact(
                dimension="pre_extraction_intake_decision",
                label=decision,
                confidence=round(confidence, 4),
                schema_version="pre_extraction_intake_v1",
                paper_id=intake.paper_id,
                bundle_id=primary_bundle_id,
                topic_label=primary_topic,
                edge_case_kind=edge_case_kind,
                novelty_signal=round(novelty_signal, 4),
                details_json={
                    "paper_id": intake.paper_id,
                    "processing_stage": intake.processing_stage,
                    "available_evidence_types": list(intake.available_evidence_types),
                    "routing_target": routing_target,
                    "domain_relevance": domain_relevance,
                    "topic_candidates": list(topic_candidates),
                    "matched_question_ids": list(matched_question_ids),
                    "topic_expansion_candidate": topic_expansion_candidate,
                    "new_topic_candidate": new_topic_candidate,
                    "proposed_topic_label": proposed_topic_label,
                    "reasons": list(reasons),
                },
            ),
        ]
        if primary_topic:
            facts.append(
                RegistryFact(
                    dimension="topic_routing_preliminary",
                    label=primary_topic,
                    confidence=round(confidence, 4),
                    schema_version="pre_extraction_intake_v1",
                    paper_id=intake.paper_id,
                    bundle_id=primary_bundle_id,
                    topic_label=primary_topic,
                    details_json={
                        "paper_id": intake.paper_id,
                        "topic_candidates": list(topic_candidates),
                        "matched_question_ids": list(matched_question_ids),
                    },
                )
            )
        if topic_expansion_candidate or new_topic_candidate:
            facts.append(
                RegistryFact(
                    dimension="novelty_preservation",
                    label="new_topic_candidate" if new_topic_candidate else "topic_expansion_candidate",
                    confidence=round(max(novelty_signal, confidence), 4),
                    schema_version="pre_extraction_intake_v1",
                    paper_id=intake.paper_id,
                    edge_case_kind=edge_case_kind,
                    novelty_signal=round(novelty_signal, 4),
                    details_json={
                        "paper_id": intake.paper_id,
                        "proposed_topic_label": proposed_topic_label,
                        "topic_expansion_candidate": topic_expansion_candidate,
                        "new_topic_candidate": new_topic_candidate,
                        "routing_target": routing_target,
                    },
                )
            )
        return tuple(facts)
