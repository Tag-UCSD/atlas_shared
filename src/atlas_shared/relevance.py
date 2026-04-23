from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Literal, Mapping, Protocol, Sequence

from .article_types import ArticleTypeDecision, HeuristicArticleTypeClassifier
from .registry_sink import SupportsClassificationRegistry


STATS_RE = re.compile(
    r"\b(?:p\s*[<=>]\s*\.?\d+|anova|regression|t-test|randomi[sz]ed|between-subject|within-subject|n\s*=)\b",
    re.IGNORECASE,
)
NEGATION_RE = re.compile(
    r"\b(?:no|not|without|lacks?|lacked|lacking|absent|absence of|did not|does not|was not|were not|never)\b",
    re.IGNORECASE,
)


class SupportsArticleTypeClassification(Protocol):
    def classify(self, *, abstract: str = "", title: str = "", keywords: Sequence[str] = ()) -> Any: ...


class SupportsRelevanceAdjudication(Protocol):
    def adjudicate(self, request: "AdjudicationRequest") -> "AdjudicationResult | None": ...


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")
    return cleaned or "unknown"


def _norm(text: str | None) -> str:
    return str(text or "").strip().lower()


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    phrase = _norm(phrase)
    parts = [part for part in phrase.split() if part]
    pattern_parts: list[str] = []
    for index, part in enumerate(parts):
        escaped = re.escape(part)
        if index == len(parts) - 1 and part.isalpha() and not part.endswith("s"):
            escaped = f"{escaped}s?"
        pattern_parts.append(escaped)
    escaped = r"[\s\-]+".join(pattern_parts)
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def _is_negated(text: str, start: int) -> bool:
    window = text[max(0, start - 32):start]
    return bool(NEGATION_RE.search(window))


def _contains_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    for match in _phrase_pattern(phrase).finditer(text):
        if not _is_negated(text, match.start()):
            return True
    return False


def _find_hits(text: str, phrases: Sequence[str]) -> list[str]:
    hits: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        norm = _norm(phrase)
        if not norm or norm in seen:
            continue
        if _contains_phrase(text, norm):
            hits.append(norm)
            seen.add(norm)
    return hits


def _split_terms(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, Sequence):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _normalize_classifier_output(result: Any) -> ArticleTypeDecision:
    if isinstance(result, ArticleTypeDecision):
        return result

    article_type = getattr(result, "article_type", None)
    if article_type is not None:
        value = getattr(article_type, "value", article_type)
        return ArticleTypeDecision(
            value=str(value),
            confidence=float(getattr(result, "confidence", 0.0)),
            source=str(getattr(result, "source", "external_classifier")),
            evidence=tuple(getattr(result, "evidence", ()) or ()),
        )

    value = getattr(result, "value", None)
    if value is not None:
        return ArticleTypeDecision(
            value=str(value),
            confidence=float(getattr(result, "confidence", 0.0)),
            source=str(getattr(result, "source", "external_classifier")),
            evidence=tuple(getattr(result, "evidence", ()) or ()),
        )

    raise TypeError("Unsupported article-type classifier output")


@dataclass(frozen=True)
class QuestionConstitution:
    question_id: str
    question_text: str
    topic: str = ""
    panel_status: str = "draft"
    constitution_version: str = "v0"
    environment_terms: tuple[str, ...] = ()
    outcome_terms: tuple[str, ...] = ()
    exclusion_terms: tuple[str, ...] = ()
    edge_terms: tuple[str, ...] = ()
    search_hints: tuple[str, ...] = ()
    accept_indicators: tuple[str, ...] = ()
    reject_indicators: tuple[str, ...] = ()
    edge_case_indicators: tuple[str, ...] = ()
    allowed_article_types: tuple[str, ...] = (
        "empirical_research",
        "systematic_review",
        "meta_analysis",
        "narrative_review",
        "case_study",
        "mixed_methods",
        "qualitative_research",
        "qualitative",
    )
    marginal_article_types: tuple[str, ...] = (
        "theoretical",
        "commentary",
        "protocol",
    )
    rejected_article_types: tuple[str, ...] = (
        "book_review",
        "editorial",
        "preprint",
        "computational_simulation",
    )
    required_evidence_terms: tuple[str, ...] = ()

    @classmethod
    def from_panel_spec(cls, spec: Mapping[str, Any]) -> "QuestionConstitution":
        return cls(
            question_id=str(spec.get("question_id") or spec.get("id") or "question"),
            question_text=str(spec.get("question_text") or spec.get("question") or ""),
            topic=str(spec.get("topic") or ""),
            panel_status=str(spec.get("panel_status") or "draft"),
            constitution_version=str(spec.get("constitution_version") or spec.get("version") or "v0"),
            environment_terms=tuple(_split_terms(spec.get("environment_terms") or spec.get("iv_terms"))),
            outcome_terms=tuple(_split_terms(spec.get("outcome_terms") or spec.get("dv_terms"))),
            exclusion_terms=tuple(_split_terms(spec.get("exclusion_terms") or spec.get("false_friends"))),
            edge_terms=tuple(_split_terms(spec.get("edge_terms") or spec.get("near_misses"))),
            search_hints=tuple(_split_terms(spec.get("search_hints"))),
            accept_indicators=tuple(_split_terms(spec.get("accept_indicators") or spec.get("in_criteria"))),
            reject_indicators=tuple(_split_terms(spec.get("reject_indicators") or spec.get("out_criteria"))),
            edge_case_indicators=tuple(_split_terms(spec.get("edge_case_indicators") or spec.get("hard_case_criteria"))),
            allowed_article_types=tuple(_split_terms(spec.get("allowed_article_types"))) or cls.allowed_article_types,
            marginal_article_types=tuple(_split_terms(spec.get("marginal_article_types"))) or cls.marginal_article_types,
            rejected_article_types=tuple(_split_terms(spec.get("rejected_article_types"))) or cls.rejected_article_types,
            required_evidence_terms=tuple(_split_terms(spec.get("required_evidence_terms"))),
        )

    @property
    def bundle_id(self) -> str:
        stem = self.topic or self.question_text or self.question_id
        return f"bundle-{_slug(stem)}-{_slug(self.question_id)}"


@dataclass(frozen=True)
class ArticleCandidate:
    paper_id: str
    title: str
    abstract: str = ""
    article_type: str = ""
    year: int | None = None
    keywords: tuple[str, ...] = ()
    body_text: str = ""

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "ArticleCandidate":
        body_chunks = [
            str(obj.get("body_text") or obj.get("full_text") or ""),
            str(obj.get("first_page_text") or obj.get("page_1_text") or ""),
            str(obj.get("methods_surface_summary") or ""),
        ]
        summary = obj.get("science_writer_summary")
        if isinstance(summary, Mapping):
            sections = summary.get("sections")
            if isinstance(sections, Mapping):
                body_chunks.extend(str(value or "") for value in sections.values())
        elif summary:
            body_chunks.append(str(summary))
        for key in ("independent_variables", "dependent_variables", "iv_raw", "dv_raw", "iv_mapped", "dv_mapped"):
            body_chunks.append(str(obj.get(key) or ""))
        inventory = obj.get("measurement_inventory")
        if isinstance(inventory, Sequence) and not isinstance(inventory, (str, bytes)):
            for item in inventory:
                if not isinstance(item, Mapping):
                    continue
                for key in ("outcome", "measure_name", "instrument_name", "instrument_type", "sensor_name", "sensor_type"):
                    body_chunks.append(str(item.get(key) or ""))
        return cls(
            paper_id=str(obj.get("paper_id") or obj.get("id") or ""),
            title=str(obj.get("title") or ""),
            abstract=str(obj.get("abstract") or ""),
            article_type=str(obj.get("article_type") or ""),
            year=obj.get("year") if isinstance(obj.get("year"), int) else None,
            keywords=tuple(_split_terms(obj.get("keywords"))) + tuple(_split_terms(obj.get("topic_hints"))),
            body_text="\n".join(chunk for chunk in body_chunks if chunk.strip()),
        )


@dataclass(frozen=True)
class RelevanceAssessment:
    paper_id: str
    question_id: str
    bundle_id: str
    article_type: ArticleTypeDecision
    verdict: str
    confidence: float
    needs_manual_review: bool
    environment_hits: tuple[str, ...] = ()
    outcome_hits: tuple[str, ...] = ()
    exclusion_hits: tuple[str, ...] = ()
    edge_hits: tuple[str, ...] = ()
    evidence_hits: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    adjudication_source: str = "heuristic_filter"
    edge_case_kind: str = "none"
    novelty_signal: float = 0.0
    topic_expansion_candidate: bool = False
    new_topic_candidate: bool = False
    proposed_topic_label: str = ""
    adjacent_topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class AdjudicationRequest:
    constitution: QuestionConstitution
    article: ArticleCandidate
    heuristic_assessment: RelevanceAssessment


@dataclass(frozen=True)
class AdjudicationResult:
    verdict: Literal["accept", "edge_case", "reject"]
    confidence: float
    reasons: tuple[str, ...] = ()
    needs_manual_review: bool = False
    source: str = "llm_panel"
    edge_case_kind: str = "none"
    novelty_signal: float = 0.0
    topic_expansion_candidate: bool = False
    new_topic_candidate: bool = False
    proposed_topic_label: str = ""
    adjacent_topics: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArticleBundle:
    bundle_id: str
    question_id: str
    question_text: str
    topic: str
    accepted: tuple[RelevanceAssessment, ...] = ()
    edge_cases: tuple[RelevanceAssessment, ...] = ()
    rejected: tuple[RelevanceAssessment, ...] = ()


class QuestionArticleRelevanceFilter:
    def __init__(
        self,
        *,
        classifier: SupportsArticleTypeClassification | None = None,
        adjudicator: SupportsRelevanceAdjudication | None = None,
        registry_sink: SupportsClassificationRegistry | None = None,
        adjudication_policy: Literal["never", "borderline_only", "always"] = "borderline_only",
    ) -> None:
        self.classifier = classifier or HeuristicArticleTypeClassifier()
        self.adjudicator = adjudicator
        self.registry_sink = registry_sink
        self.adjudication_policy = adjudication_policy
        self._recorded_article_types: set[str] = set()
        self._recorded_question_assessments: set[tuple[str, str]] = set()

    def classify_article_type(self, article: ArticleCandidate) -> ArticleTypeDecision:
        explicit = _norm(article.article_type)
        if explicit and explicit != "unknown":
            decision = ArticleTypeDecision(
                value=explicit,
                confidence=1.0,
                source="article_record",
                evidence=("article_type already present on record",),
            )
            self._record_article_type(article, decision)
            return decision
        raw = self.classifier.classify(
            abstract=article.abstract or article.body_text[:3000],
            title=article.title,
            keywords=list(article.keywords),
        )
        decision = _normalize_classifier_output(raw)
        self._record_article_type(article, decision)
        return decision

    def assess(self, constitution: QuestionConstitution, article: ArticleCandidate) -> RelevanceAssessment:
        article_type = self.classify_article_type(article)
        combined_text = "\n".join(
            piece for piece in (
                article.title,
                article.abstract,
                " ".join(article.keywords),
                article.body_text[:6000],
            )
            if piece
        ).lower()

        environment_hits = tuple(_find_hits(combined_text, constitution.environment_terms))
        outcome_hits = tuple(_find_hits(combined_text, constitution.outcome_terms))
        exclusion_hits = tuple(_find_hits(combined_text, constitution.exclusion_terms))
        edge_hits = tuple(_find_hits(combined_text, constitution.edge_terms))
        evidence_hits = tuple(
            _find_hits(combined_text, constitution.required_evidence_terms + constitution.search_hints)
        )

        reasons: list[str] = []
        verdict = "reject"
        confidence = 0.15
        needs_manual_review = False

        if article_type.value in constitution.rejected_article_types:
            reasons.append(f"article type {article_type.value} is explicitly rejected for this question")
            return self._record_question_assessment(
                article,
                constitution,
                RelevanceAssessment(
                paper_id=article.paper_id,
                question_id=constitution.question_id,
                bundle_id=constitution.bundle_id,
                article_type=article_type,
                verdict="reject",
                confidence=0.95,
                needs_manual_review=False,
                environment_hits=environment_hits,
                outcome_hits=outcome_hits,
                exclusion_hits=exclusion_hits,
                edge_hits=edge_hits,
                evidence_hits=evidence_hits,
                reasons=tuple(reasons),
                edge_case_kind="none",
                ),
            )

        if exclusion_hits:
            reasons.append(f"false-friend or exclusion hits: {', '.join(exclusion_hits)}")
            return self._record_question_assessment(
                article,
                constitution,
                RelevanceAssessment(
                paper_id=article.paper_id,
                question_id=constitution.question_id,
                bundle_id=constitution.bundle_id,
                article_type=article_type,
                verdict="reject",
                confidence=0.92,
                needs_manual_review=False,
                environment_hits=environment_hits,
                outcome_hits=outcome_hits,
                exclusion_hits=exclusion_hits,
                edge_hits=edge_hits,
                evidence_hits=evidence_hits,
                reasons=tuple(reasons),
                edge_case_kind="none",
                ),
            )

        env_ok = bool(environment_hits)
        out_ok = bool(outcome_hits)
        empirical_support = bool(STATS_RE.search(combined_text) or evidence_hits)

        if env_ok and out_ok:
            reasons.append(f"matches environment side: {', '.join(environment_hits)}")
            reasons.append(f"matches outcome side: {', '.join(outcome_hits)}")
            if article_type.value in constitution.marginal_article_types:
                verdict = "edge_case"
                confidence = 0.72
                needs_manual_review = True
                reasons.append(f"article type {article_type.value} is marginal for this question")
            elif constitution.required_evidence_terms and not evidence_hits and article_type.value == "empirical_research":
                verdict = "edge_case"
                confidence = 0.66
                needs_manual_review = True
                reasons.append("topic match is present, but required evidence markers were not found")
            elif article_type.value in constitution.allowed_article_types or article_type.value == "empirical_research":
                verdict = "accept"
                confidence = 0.90 if empirical_support else 0.82
            else:
                verdict = "edge_case"
                confidence = 0.70
                needs_manual_review = True
                reasons.append(f"article type {article_type.value} is not explicitly allowed")
        elif env_ok or out_ok:
            verdict = "edge_case"
            confidence = 0.58
            needs_manual_review = True
            if env_ok:
                reasons.append(f"matches environment side only: {', '.join(environment_hits)}")
            if out_ok:
                reasons.append(f"matches outcome side only: {', '.join(outcome_hits)}")
            reasons.append("partial construct overlap; likely adjacent or near-miss article")
        elif edge_hits:
            verdict = "edge_case"
            confidence = 0.50
            needs_manual_review = True
            reasons.append(f"edge-case terms present: {', '.join(edge_hits)}")
        else:
            verdict = "reject"
            confidence = 0.88
            reasons.append("no adequate environment/outcome overlap with the question constitution")

        heuristic = RelevanceAssessment(
            paper_id=article.paper_id,
            question_id=constitution.question_id,
            bundle_id=constitution.bundle_id,
            article_type=article_type,
            verdict=verdict,
            confidence=confidence,
            needs_manual_review=needs_manual_review,
            environment_hits=environment_hits,
            outcome_hits=outcome_hits,
            exclusion_hits=exclusion_hits,
            edge_hits=edge_hits,
            evidence_hits=evidence_hits,
            reasons=tuple(reasons),
            edge_case_kind="undetermined" if verdict == "edge_case" else "none",
        )
        return self._record_question_assessment(
            article,
            constitution,
            self._maybe_adjudicate(constitution, article, heuristic),
        )

    def _maybe_adjudicate(
        self,
        constitution: QuestionConstitution,
        article: ArticleCandidate,
        heuristic: RelevanceAssessment,
    ) -> RelevanceAssessment:
        if self.adjudicator is None or self.adjudication_policy == "never":
            return heuristic

        should_adjudicate = self.adjudication_policy == "always"
        if self.adjudication_policy == "borderline_only":
            should_adjudicate = (
                heuristic.verdict == "edge_case"
                or heuristic.confidence < 0.75
                or heuristic.needs_manual_review
            )

        if not should_adjudicate:
            return heuristic

        result = self.adjudicator.adjudicate(
            AdjudicationRequest(
                constitution=constitution,
                article=article,
                heuristic_assessment=heuristic,
            )
        )
        if result is None:
            return heuristic

        return RelevanceAssessment(
            paper_id=heuristic.paper_id,
            question_id=heuristic.question_id,
            bundle_id=heuristic.bundle_id,
            article_type=heuristic.article_type,
            verdict=result.verdict,
            confidence=result.confidence,
            needs_manual_review=result.needs_manual_review,
            environment_hits=heuristic.environment_hits,
            outcome_hits=heuristic.outcome_hits,
            exclusion_hits=heuristic.exclusion_hits,
            edge_hits=heuristic.edge_hits,
            evidence_hits=heuristic.evidence_hits,
            reasons=tuple(heuristic.reasons) + tuple(result.reasons),
            adjudication_source=result.source,
            edge_case_kind=result.edge_case_kind,
            novelty_signal=result.novelty_signal,
            topic_expansion_candidate=result.topic_expansion_candidate,
            new_topic_candidate=result.new_topic_candidate,
            proposed_topic_label=result.proposed_topic_label,
            adjacent_topics=result.adjacent_topics,
        )

    def build_article_bundle(
        self,
        constitution: QuestionConstitution,
        articles: Iterable[ArticleCandidate | Mapping[str, Any]],
    ) -> ArticleBundle:
        accepted: list[RelevanceAssessment] = []
        edge_cases: list[RelevanceAssessment] = []
        rejected: list[RelevanceAssessment] = []

        for article_like in articles:
            article = article_like if isinstance(article_like, ArticleCandidate) else ArticleCandidate.from_mapping(article_like)
            assessment = self.assess(constitution, article)
            if assessment.verdict == "accept":
                accepted.append(assessment)
            elif assessment.verdict == "edge_case":
                edge_cases.append(assessment)
            else:
                rejected.append(assessment)

        accepted.sort(key=lambda item: (-item.confidence, item.paper_id))
        edge_cases.sort(key=lambda item: (-item.confidence, item.paper_id))
        rejected.sort(key=lambda item: (-item.confidence, item.paper_id))

        return ArticleBundle(
            bundle_id=constitution.bundle_id,
            question_id=constitution.question_id,
            question_text=constitution.question_text,
            topic=constitution.topic,
            accepted=tuple(accepted),
            edge_cases=tuple(edge_cases),
            rejected=tuple(rejected),
        )

    def _record_article_type(self, article: ArticleCandidate, decision: ArticleTypeDecision) -> None:
        if self.registry_sink is None or not article.paper_id:
            return
        if article.paper_id in self._recorded_article_types:
            return
        self.registry_sink.record_article_type(article, decision)
        self._recorded_article_types.add(article.paper_id)

    def _record_question_assessment(
        self,
        article: ArticleCandidate,
        constitution: QuestionConstitution,
        assessment: RelevanceAssessment,
    ) -> RelevanceAssessment:
        if self.registry_sink is None or not article.paper_id:
            return assessment
        key = (article.paper_id, constitution.question_id)
        if key in self._recorded_question_assessments:
            return assessment
        self.registry_sink.record_question_assessment(article, constitution, assessment)
        self._recorded_question_assessments.add(key)
        return assessment
