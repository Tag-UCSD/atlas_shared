from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import subprocess
from typing import Any, Literal, Mapping, Protocol, Sequence

from ._util import _assessment_weight, _split_terms
from .article_types import ArticleTypeDecision, HeuristicArticleTypeClassifier, clean_article_type_text
from .bundle_router import BundleRoutingResult, TopicBundleCandidate
from .intake import PreExtractionIntakeGate, PreExtractionIntakeResult
from .registry_sink import SupportsClassificationRegistry
from .relevance import (
    ArticleCandidate,
    QuestionArticleRelevanceFilter,
    QuestionConstitution,
    RelevanceAssessment,
    SupportsArticleTypeClassification,
    SupportsRelevanceAdjudication,
)
from .topic_bank import load_topic_constitution_bank


EvidenceStage = Literal[
    "bibliographic_only",
    "metadata_text",
    "pdf_surface_light",
    "extraction_aware",
]

NextAction = Literal[
    "need_abstract_or_keywords",
    "extract_pdf_surface",
    "review_borderline_case",
    "ready_for_intake_decision",
    "ready_for_downstream_extraction",
    "ready_for_topic_routing",
]


HEADING_KEYWORDS: tuple[str, ...] = (
    "abstract",
    "introduction",
    "background",
    "methods",
    "method",
    "materials and methods",
    "procedure",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "references",
)
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


def _unique_strings(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = str(value or "").strip()
        if not cleaned or cleaned in seen:
            continue
        ordered.append(cleaned)
        seen.add(cleaned)
    return tuple(ordered)
def _verdict_rank(verdict: str) -> int:
    order = {"reject": 0, "edge_case": 1, "accept": 2}
    return order.get(verdict, -1)


def _article_text(evidence: "ClassificationEvidence") -> str:
    parts = [
        evidence.title,
        evidence.abstract,
        " ".join(evidence.keywords),
        " ".join(evidence.zotero_tags),
        evidence.first_page_text,
        evidence.surface_snapshot.raw_text if evidence.surface_snapshot else "",
        evidence.surface_snapshot.intro_excerpt if evidence.surface_snapshot else "",
        evidence.surface_snapshot.methods_excerpt if evidence.surface_snapshot else "",
        evidence.surface_snapshot.conclusion_excerpt if evidence.surface_snapshot else "",
        evidence.methods_surface_summary,
        _summary_to_text(evidence.science_writer_summary),
        " ".join(evidence.independent_variables),
        " ".join(evidence.dependent_variables),
        " ".join(evidence.measurement_terms),
        " ".join(evidence.instrument_terms),
        " ".join(evidence.sensor_terms),
        " ".join(evidence.topic_hints),
    ]
    return "\n".join(part for part in parts if str(part or "").strip())


def _section_excerpt(text: str, headings: Sequence[str], *, max_chars: int = 1200) -> str:
    if not text.strip():
        return ""
    lines = [line.rstrip() for line in text.splitlines()]
    normalized_headings = {heading.lower() for heading in headings}
    start = None
    for index, line in enumerate(lines):
        cleaned = re.sub(r"^[0-9.\s]+", "", line.strip()).lower()
        if cleaned in normalized_headings:
            start = index + 1
            break
    if start is None:
        return ""

    collected: list[str] = []
    for line in lines[start:]:
        cleaned = re.sub(r"^[0-9.\s]+", "", line.strip()).lower()
        if cleaned in HEADING_KEYWORDS:
            break
        if not line.strip():
            if collected:
                collected.append("")
            continue
        collected.append(line.strip())
        if len("\n".join(collected)) >= max_chars:
            break
    return "\n".join(collected).strip()[:max_chars]


def _extract_section_headings(text: str) -> tuple[str, ...]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 80:
            continue
        cleaned = re.sub(r"^[0-9.\s]+", "", stripped).strip()
        normalized = cleaned.lower()
        if normalized in HEADING_KEYWORDS:
            headings.append(cleaned)
            continue
        if cleaned.isupper() and 2 <= len(cleaned.split()) <= 6:
            headings.append(cleaned)
    return _unique_strings(headings)


@dataclass(frozen=True)
class PDFSurfaceSnapshot:
    source: str
    extraction_mode: str
    pages_read: int
    raw_text: str
    section_headings: tuple[str, ...] = ()
    first_page_excerpt: str = ""
    abstract_excerpt: str = ""
    intro_excerpt: str = ""
    methods_excerpt: str = ""
    conclusion_excerpt: str = ""
    pdf_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SupportsPDFSurfaceExtraction(Protocol):
    def extract(
        self,
        evidence: "ClassificationEvidence",
        *,
        max_pages: int = 4,
        max_chars: int = 8000,
    ) -> PDFSurfaceSnapshot | None: ...


@dataclass(frozen=True)
class TopicOverlayRecord:
    topic_id: str
    label: str
    description: str = ""
    keywords: tuple[str, ...] = ()
    inclusion_terms: tuple[str, ...] = ()
    exclusion_terms: tuple[str, ...] = ()
    source: str = "active_overlay"

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "TopicOverlayRecord":
        return cls(
            topic_id=str(obj.get("topic_id") or obj.get("id") or obj.get("label") or ""),
            label=str(obj.get("label") or obj.get("topic") or obj.get("name") or ""),
            description=str(obj.get("description") or ""),
            keywords=_split_terms(obj.get("keywords")),
            inclusion_terms=_split_terms(obj.get("inclusion_terms") or obj.get("terms")),
            exclusion_terms=_split_terms(obj.get("exclusion_terms")),
            source=str(obj.get("source") or "active_overlay"),
        )


@dataclass(frozen=True)
class TopicOverlayMatch:
    topic_id: str
    label: str
    score: float
    matched_terms: tuple[str, ...] = ()
    exclusion_hits: tuple[str, ...] = ()
    source: str = "heuristic_overlay_matcher"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SupportsTopicOverlayMatching(Protocol):
    def match(
        self,
        evidence: "ClassificationEvidence",
        topics: Sequence[TopicOverlayRecord],
        *,
        limit: int = 5,
    ) -> tuple[TopicOverlayMatch, ...]: ...


@dataclass
class ClassificationEvidence:
    paper_id: str
    title: str = ""
    abstract: str = ""
    keywords: tuple[str, ...] = ()
    doi: str = ""
    filename: str = ""
    authors: tuple[str, ...] = ()
    year: int | None = None
    zotero_tags: tuple[str, ...] = ()
    pdf_path: str = ""
    first_page_text: str = ""
    preliminary_article_type: str = ""
    methods_surface_summary: str = ""
    science_writer_summary: str | Mapping[str, Any] = ""
    independent_variables: tuple[str, ...] = ()
    dependent_variables: tuple[str, ...] = ()
    measurement_terms: tuple[str, ...] = ()
    instrument_terms: tuple[str, ...] = ()
    sensor_terms: tuple[str, ...] = ()
    topic_hints: tuple[str, ...] = ()
    surface_snapshot: PDFSurfaceSnapshot | None = None

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any]) -> "ClassificationEvidence":
        measurement_inventory = obj.get("measurement_inventory")
        measurement_terms: list[str] = []
        instrument_terms: list[str] = []
        sensor_terms: list[str] = []
        if isinstance(measurement_inventory, Sequence) and not isinstance(measurement_inventory, (str, bytes)):
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
            paper_id=str(obj.get("paper_id") or obj.get("id") or ""),
            title=str(obj.get("title") or ""),
            abstract=str(obj.get("abstract") or ""),
            keywords=_split_terms(obj.get("keywords")),
            doi=str(obj.get("doi") or ""),
            filename=str(obj.get("filename") or obj.get("file_name") or ""),
            authors=_split_terms(obj.get("authors")),
            year=obj.get("year") if isinstance(obj.get("year"), int) else None,
            zotero_tags=_split_terms(obj.get("zotero_tags") or obj.get("tags")),
            pdf_path=str(obj.get("pdf_path") or ""),
            first_page_text=str(obj.get("first_page_text") or obj.get("page_1_text") or ""),
            preliminary_article_type=str(obj.get("article_type") or obj.get("preliminary_article_type") or ""),
            methods_surface_summary=str(obj.get("methods_surface_summary") or ""),
            science_writer_summary=obj.get("science_writer_summary") or "",
            independent_variables=_split_terms(
                obj.get("independent_variables") or obj.get("iv_raw") or obj.get("iv_mapped")
            ),
            dependent_variables=_split_terms(
                obj.get("dependent_variables") or obj.get("dv_raw") or obj.get("dv_mapped")
            ),
            measurement_terms=tuple(measurement_terms) or _split_terms(obj.get("measurement_terms")),
            instrument_terms=tuple(instrument_terms) or _split_terms(obj.get("instrument_terms")),
            sensor_terms=tuple(sensor_terms) or _split_terms(obj.get("sensor_terms")),
            topic_hints=_split_terms(obj.get("topic_hints") or obj.get("topics") or obj.get("topic_candidates")),
        )

    @property
    def available_evidence_types(self) -> tuple[str, ...]:
        evidence_types: list[str] = []
        for name, value in (
            ("title", self.title),
            ("abstract", self.abstract),
            ("keywords", self.keywords),
            ("zotero_tags", self.zotero_tags),
            ("first_page_text", self.first_page_text),
            ("pdf_path", self.pdf_path),
            ("surface_snapshot", self.surface_snapshot),
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
                evidence_types.append(name)
        return tuple(evidence_types)

    @property
    def inferred_stage(self) -> EvidenceStage:
        if any(
            (
                self.methods_surface_summary,
                _summary_to_text(self.science_writer_summary),
                self.independent_variables,
                self.dependent_variables,
                self.measurement_terms,
                self.instrument_terms,
                self.sensor_terms,
                self.topic_hints,
            )
        ):
            return "extraction_aware"
        if self.surface_snapshot is not None or self.first_page_text:
            return "pdf_surface_light"
        if self.abstract or self.keywords:
            return "metadata_text"
        return "bibliographic_only"

    @property
    def has_pdf_available(self) -> bool:
        return bool(self.pdf_path)

    @property
    def text_for_classification(self) -> str:
        return _article_text(self)

    def to_article_candidate(self) -> ArticleCandidate:
        return ArticleCandidate(
            paper_id=self.paper_id,
            title=self.title,
            abstract=self.abstract,
            article_type=self.preliminary_article_type,
            year=self.year,
            keywords=_unique_strings(self.keywords + self.topic_hints),
            body_text=self.text_for_classification,
        )

    def to_pre_extraction_mapping(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "filename": self.filename,
            "doi": self.doi,
            "zotero_tags": list(self.zotero_tags),
            "keywords": list(self.keywords),
            "first_page_text": self.first_page_text or (
                self.surface_snapshot.first_page_excerpt if self.surface_snapshot else ""
            ),
            "article_type": self.preliminary_article_type,
            "pdf_path": self.pdf_path,
            "methods_surface_summary": self.methods_surface_summary,
            "science_writer_summary": self.science_writer_summary,
            "independent_variables": list(self.independent_variables),
            "dependent_variables": list(self.dependent_variables),
            "measurement_terms": list(self.measurement_terms),
            "instrument_terms": list(self.instrument_terms),
            "sensor_terms": list(self.sensor_terms),
            "topic_hints": list(self.topic_hints),
        }

    def with_surface_snapshot(self, snapshot: PDFSurfaceSnapshot) -> "ClassificationEvidence":
        return ClassificationEvidence(
            paper_id=self.paper_id,
            title=self.title,
            abstract=self.abstract,
            keywords=self.keywords,
            doi=self.doi,
            filename=self.filename,
            authors=self.authors,
            year=self.year,
            zotero_tags=self.zotero_tags,
            pdf_path=self.pdf_path,
            first_page_text=self.first_page_text or snapshot.first_page_excerpt,
            preliminary_article_type=self.preliminary_article_type,
            methods_surface_summary=self.methods_surface_summary,
            science_writer_summary=self.science_writer_summary,
            independent_variables=self.independent_variables,
            dependent_variables=self.dependent_variables,
            measurement_terms=self.measurement_terms,
            instrument_terms=self.instrument_terms,
            sensor_terms=self.sensor_terms,
            topic_hints=self.topic_hints,
            surface_snapshot=snapshot,
        )


@dataclass(frozen=True)
class ClassificationStageRecord:
    name: str
    reason: str
    confidence: float = 0.0
    created_evidence: bool = False
    evidence_types: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuestionSummary:
    enabled: bool
    questions_considered: int
    best_question_id: str | None = None
    best_bundle_id: str | None = None
    best_verdict: str | None = None
    best_confidence: float = 0.0
    needs_manual_review: bool = False
    best_edge_case_kind: str = "none"
    max_novelty_signal: float = 0.0
    topic_expansion_candidate_count: int = 0
    new_topic_candidate_count: int = 0
    proposed_topic_labels: tuple[str, ...] = ()
    accepted_question_ids: tuple[str, ...] = ()
    edge_case_question_ids: tuple[str, ...] = ()
    rejected_question_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdaptiveClassificationResult:
    paper_id: str
    evidence_stage: EvidenceStage
    available_evidence_types: tuple[str, ...]
    article_type: ArticleTypeDecision
    intake_result: PreExtractionIntakeResult | None
    question_summary: QuestionSummary
    stable_topic_routing: BundleRoutingResult | None
    active_topic_matches: tuple[TopicOverlayMatch, ...]
    surface_snapshot: PDFSurfaceSnapshot | None
    analysis_steps_run: tuple[str, ...]
    stage_history: tuple[ClassificationStageRecord, ...]
    next_action: NextAction
    needs_more_evidence: bool
    overall_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "evidence_stage": self.evidence_stage,
            "available_evidence_types": list(self.available_evidence_types),
            "article_type": asdict(self.article_type),
            "intake_result": self.intake_result.to_dict() if self.intake_result else None,
            "question_summary": self.question_summary.to_dict(),
            "stable_topic_routing": asdict(self.stable_topic_routing) if self.stable_topic_routing else None,
            "active_topic_matches": [item.to_dict() for item in self.active_topic_matches],
            "surface_snapshot": self.surface_snapshot.to_dict() if self.surface_snapshot else None,
            "analysis_steps_run": list(self.analysis_steps_run),
            "stage_history": [item.to_dict() for item in self.stage_history],
            "next_action": self.next_action,
            "needs_more_evidence": self.needs_more_evidence,
            "overall_confidence": self.overall_confidence,
        }


class LocalPDFSurfaceExtractor:
    """
    Cheap PDF surface extraction for staged classification.

    This is intentionally lightweight. It prefers native text extraction and
    uses import-based fallbacks only when needed.
    """

    def extract(
        self,
        evidence: ClassificationEvidence,
        *,
        max_pages: int = 16,
        max_chars: int = 30000,
    ) -> PDFSurfaceSnapshot | None:
        if not evidence.pdf_path:
            return None

        pdf_path = Path(evidence.pdf_path)
        if not pdf_path.exists():
            return None

        text = ""
        mode = ""
        try:
            result = subprocess.run(
                ["pdftotext", "-f", "1", "-l", str(max_pages), str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                text = clean_article_type_text(result.stdout)[:max_chars]
                mode = "pdftotext"
        except FileNotFoundError:
            pass
        except Exception:
            pass

        if not text:
            for module_name in ("pypdf", "PyPDF2"):
                try:
                    module = __import__(module_name, fromlist=["PdfReader"])
                    reader = module.PdfReader(str(pdf_path))
                    parts: list[str] = []
                    for page in reader.pages[:max_pages]:
                        parts.append(page.extract_text() or "")
                        if len("\n".join(parts)) >= max_chars:
                            break
                    text = clean_article_type_text("\n".join(parts))[:max_chars]
                    mode = module_name
                    if text.strip():
                        break
                except Exception:
                    continue

        if not text.strip():
            return None

        section_headings = _extract_section_headings(text)
        intro_excerpt = _section_excerpt(text, ("introduction", "background")) or text[:1200].strip()
        methods_excerpt = _section_excerpt(text, ("methods", "method", "materials and methods", "procedure"))
        conclusion_excerpt = _section_excerpt(text, ("conclusion", "conclusions", "discussion"))
        abstract_excerpt = _section_excerpt(text, ("abstract",))

        return PDFSurfaceSnapshot(
            source="atlas_shared.classifier_system.LocalPDFSurfaceExtractor",
            extraction_mode=mode or "unknown",
            pages_read=max_pages,
            raw_text=text,
            section_headings=section_headings,
            first_page_excerpt=text[:1200].strip(),
            abstract_excerpt=abstract_excerpt,
            intro_excerpt=intro_excerpt,
            methods_excerpt=methods_excerpt,
            conclusion_excerpt=conclusion_excerpt,
            pdf_path=str(pdf_path),
        )


class HeuristicTopicOverlayMatcher:
    def _phrase_hits(self, text: str, phrases: Sequence[str]) -> tuple[str, ...]:
        hits: list[str] = []
        lowered = text.lower()
        for phrase in phrases:
            cleaned = str(phrase or "").strip().lower()
            if not cleaned:
                continue
            pattern = re.escape(cleaned).replace(r"\ ", r"[\s\-]+")
            if re.search(rf"\b{pattern}\b", lowered, re.IGNORECASE):
                hits.append(cleaned)
        return _unique_strings(hits)

    def match(
        self,
        evidence: ClassificationEvidence,
        topics: Sequence[TopicOverlayRecord],
        *,
        limit: int = 5,
    ) -> tuple[TopicOverlayMatch, ...]:
        text = evidence.text_for_classification.lower()
        if not text.strip():
            return ()

        matches: list[TopicOverlayMatch] = []
        for topic in topics:
            candidate_terms = _unique_strings((topic.label,) + topic.keywords + topic.inclusion_terms)
            hits = self._phrase_hits(text, candidate_terms)
            exclusion_hits = self._phrase_hits(text, topic.exclusion_terms)
            if not hits and topic.description:
                description_hits = self._phrase_hits(text, _split_terms(topic.description))
                hits = _unique_strings(hits + description_hits)

            if not hits:
                continue

            score = 0.24 + 0.12 * len(hits)
            if topic.label.lower() in hits:
                score += 0.08
            score -= 0.12 * len(exclusion_hits)
            if score <= 0.2:
                continue

            matches.append(
                TopicOverlayMatch(
                    topic_id=topic.topic_id or topic.label,
                    label=topic.label,
                    score=round(min(score, 0.96), 4),
                    matched_terms=hits,
                    exclusion_hits=exclusion_hits,
                    source=topic.source or "active_overlay",
                )
            )

        matches.sort(key=lambda item: (-item.score, -len(item.matched_terms), item.label))
        return tuple(matches[:limit])


class AdaptiveClassifierSubsystem:
    """
    Canonical staged paper classifier shared across Atlas repos.

    It uses the best evidence currently available and can create a lightweight
    PDF surface when that is the cheapest next precision step.
    """

    def __init__(
        self,
        constitutions: Sequence[QuestionConstitution] | None = None,
        *,
        classifier: SupportsArticleTypeClassification | None = None,
        adjudicator: SupportsRelevanceAdjudication | None = None,
        registry_sink: SupportsClassificationRegistry | None = None,
        surface_extractor: SupportsPDFSurfaceExtraction | None = None,
        overlay_matcher: SupportsTopicOverlayMatching | None = None,
        adjudication_policy: Literal["never", "borderline_only", "always"] = "borderline_only",
    ) -> None:
        self.constitutions = tuple(
            constitutions if constitutions is not None else load_topic_constitution_bank().constitutions
        )
        self.registry_sink = registry_sink
        self.filter = QuestionArticleRelevanceFilter(
            classifier=classifier or HeuristicArticleTypeClassifier(),
            adjudicator=adjudicator,
            registry_sink=registry_sink,
            adjudication_policy=adjudication_policy,
        )
        self.intake_gate = PreExtractionIntakeGate(
            self.constitutions,
            classifier=classifier,
            adjudicator=adjudicator,
            adjudication_policy=adjudication_policy,
        )
        self.surface_extractor = surface_extractor or LocalPDFSurfaceExtractor()
        self.overlay_matcher = overlay_matcher or HeuristicTopicOverlayMatcher()

    def classify(
        self,
        evidence_like: ClassificationEvidence | Mapping[str, Any],
        *,
        active_topic_overlay: Sequence[TopicOverlayRecord | Mapping[str, Any]] = (),
        allow_surface_creation: bool = True,
        force_surface: bool = False,
        overlay_limit: int = 5,
    ) -> AdaptiveClassificationResult:
        evidence = (
            evidence_like
            if isinstance(evidence_like, ClassificationEvidence)
            else ClassificationEvidence.from_mapping(evidence_like)
        )

        stage_history: list[ClassificationStageRecord] = [
            ClassificationStageRecord(
                name=evidence.inferred_stage,
                reason="initial evidence stage inferred from supplied fields",
                evidence_types=evidence.available_evidence_types,
            )
        ]
        analysis_steps_run: list[str] = []

        if self._should_create_surface(evidence, force_surface=force_surface) and allow_surface_creation:
            snapshot = self.surface_extractor.extract(evidence)
            if snapshot is not None and snapshot.raw_text.strip():
                evidence = evidence.with_surface_snapshot(snapshot)
                stage_history.append(
                    ClassificationStageRecord(
                        name=evidence.inferred_stage,
                        reason="lightweight PDF surface created from local PDF access",
                        created_evidence=True,
                        evidence_types=evidence.available_evidence_types,
                    )
                )
                analysis_steps_run.append("surface_extraction")

        article = evidence.to_article_candidate()
        article_type = self.filter.classify_article_type(article)
        analysis_steps_run.append("article_type")

        assessments = self._assess_questions(article)
        if assessments:
            analysis_steps_run.append("constitutional_relevance")
        question_summary = self._build_question_summary(assessments)

        stable_topic_routing = self._build_stable_topic_routing(article.paper_id, assessments)
        if stable_topic_routing is not None:
            analysis_steps_run.append("stable_topic_routing")

        intake_result: PreExtractionIntakeResult | None = None
        if evidence.inferred_stage != "extraction_aware":
            intake_result = self.intake_gate.assess(evidence.to_pre_extraction_mapping())
            analysis_steps_run.append("conservative_intake")

        overlay_records = tuple(
            item if isinstance(item, TopicOverlayRecord) else TopicOverlayRecord.from_mapping(item)
            for item in active_topic_overlay
        )
        active_topic_matches = (
            self.overlay_matcher.match(evidence, overlay_records, limit=overlay_limit)
            if overlay_records
            else ()
        )
        if active_topic_matches:
            analysis_steps_run.append("active_topic_overlay")

        overall_confidence = max(
            article_type.confidence,
            question_summary.best_confidence,
            stable_topic_routing.candidates[0].best_confidence if stable_topic_routing and stable_topic_routing.candidates else 0.0,
            active_topic_matches[0].score if active_topic_matches else 0.0,
        )

        next_action = self._next_action(
            evidence=evidence,
            question_summary=question_summary,
            stable_topic_routing=stable_topic_routing,
            intake_result=intake_result,
            overall_confidence=overall_confidence,
        )
        needs_more_evidence = next_action in {"need_abstract_or_keywords", "extract_pdf_surface"}

        return AdaptiveClassificationResult(
            paper_id=evidence.paper_id,
            evidence_stage=evidence.inferred_stage,
            available_evidence_types=evidence.available_evidence_types,
            article_type=article_type,
            intake_result=intake_result,
            question_summary=question_summary,
            stable_topic_routing=stable_topic_routing,
            active_topic_matches=active_topic_matches,
            surface_snapshot=evidence.surface_snapshot,
            analysis_steps_run=tuple(analysis_steps_run),
            stage_history=tuple(stage_history),
            next_action=next_action,
            needs_more_evidence=needs_more_evidence,
            overall_confidence=round(overall_confidence, 4),
        )

    def _should_create_surface(self, evidence: ClassificationEvidence, *, force_surface: bool = False) -> bool:
        if not evidence.has_pdf_available or evidence.surface_snapshot is not None or evidence.first_page_text:
            return False
        if force_surface:
            return True
        return evidence.inferred_stage in {"bibliographic_only", "metadata_text"}

    def _assess_questions(self, article: ArticleCandidate) -> list[RelevanceAssessment]:
        if not self.constitutions:
            return []
        return [self.filter.assess(constitution, article) for constitution in self.constitutions]

    def _build_question_summary(self, assessments: Sequence[RelevanceAssessment]) -> QuestionSummary:
        if not assessments:
            return QuestionSummary(enabled=False, questions_considered=0)

        best = max(
            assessments,
            key=lambda item: (_verdict_rank(item.verdict), item.confidence, -len(item.exclusion_hits)),
        )
        return QuestionSummary(
            enabled=True,
            questions_considered=len(assessments),
            best_question_id=best.question_id,
            best_bundle_id=best.bundle_id,
            best_verdict=best.verdict,
            best_confidence=best.confidence,
            needs_manual_review=best.needs_manual_review,
            best_edge_case_kind=best.edge_case_kind,
            max_novelty_signal=max((item.novelty_signal for item in assessments), default=0.0),
            topic_expansion_candidate_count=sum(1 for item in assessments if item.topic_expansion_candidate),
            new_topic_candidate_count=sum(1 for item in assessments if item.new_topic_candidate),
            proposed_topic_labels=_unique_strings(
                [item.proposed_topic_label for item in assessments if item.proposed_topic_label]
            ),
            accepted_question_ids=tuple(item.question_id for item in assessments if item.verdict == "accept"),
            edge_case_question_ids=tuple(item.question_id for item in assessments if item.verdict == "edge_case"),
            rejected_question_ids=tuple(item.question_id for item in assessments if item.verdict == "reject"),
            reasons=best.reasons,
        )

    def _build_stable_topic_routing(
        self,
        paper_id: str,
        assessments: Sequence[RelevanceAssessment],
    ) -> BundleRoutingResult | None:
        if not assessments:
            return None

        topic_lookup = {constitution.question_id: constitution.topic for constitution in self.constitutions}
        topic_groups: dict[str, list[RelevanceAssessment]] = {}
        for item in assessments:
            if item.verdict == "reject":
                continue
            topic = topic_lookup.get(item.question_id) or "untitled-topic"
            topic_groups.setdefault(topic, []).append(item)

        candidates: list[TopicBundleCandidate] = []
        for topic, items in topic_groups.items():
            accepted = [item for item in items if item.verdict == "accept"]
            edges = [item for item in items if item.verdict == "edge_case"]
            expansion_items = [item for item in items if item.topic_expansion_candidate]
            new_topic_items = [item for item in items if item.new_topic_candidate]
            best = max(items, key=lambda item: (item.confidence, item.verdict == "accept"))
            proposed_topic_labels = _unique_strings(
                [item.proposed_topic_label for item in items if item.proposed_topic_label]
            )
            candidates.append(
                TopicBundleCandidate(
                    topic=topic,
                    score=round(sum(_assessment_weight(item) for item in items), 4),
                    accepted_count=len(accepted),
                    edge_case_count=len(edges),
                    topic_expansion_signal_count=len(expansion_items),
                    new_topic_signal_count=len(new_topic_items),
                    max_novelty_signal=max((item.novelty_signal for item in items), default=0.0),
                    best_question_id=best.question_id,
                    best_bundle_id=best.bundle_id,
                    best_verdict=best.verdict,
                    best_confidence=best.confidence,
                    proposed_topic_labels=proposed_topic_labels,
                    assessments=tuple(sorted(items, key=lambda item: (-item.confidence, item.question_id))),
                )
            )

        candidates.sort(
            key=lambda item: (
                -item.score,
                -item.accepted_count,
                -item.edge_case_count,
                -item.max_novelty_signal,
                -item.best_confidence,
                item.topic,
            )
        )

        primary = candidates[0] if candidates else None
        emergent = tuple(
            item
            for item in candidates
            if item.topic_expansion_signal_count > 0 or item.new_topic_signal_count > 0 or item.max_novelty_signal >= 0.65
        )
        return BundleRoutingResult(
            paper_id=paper_id,
            primary_topic=primary.topic if primary else None,
            primary_bundle_id=primary.best_bundle_id if primary else None,
            candidates=tuple(candidates),
            emergent_candidates=emergent,
            all_assessments=tuple(sorted(assessments, key=lambda item: (-item.confidence, item.question_id))),
        )

    def _next_action(
        self,
        *,
        evidence: ClassificationEvidence,
        question_summary: QuestionSummary,
        stable_topic_routing: BundleRoutingResult | None,
        intake_result: PreExtractionIntakeResult | None,
        overall_confidence: float,
    ) -> NextAction:
        if evidence.inferred_stage == "bibliographic_only":
            return "extract_pdf_surface" if evidence.has_pdf_available else "need_abstract_or_keywords"

        if evidence.inferred_stage == "metadata_text" and overall_confidence < 0.7:
            return "extract_pdf_surface" if evidence.has_pdf_available else "review_borderline_case"

        if evidence.inferred_stage == "metadata_text":
            return "ready_for_intake_decision"

        if evidence.inferred_stage == "pdf_surface_light":
            if intake_result and intake_result.intake_decision == "accept_candidate":
                return "ready_for_downstream_extraction"
            if question_summary.best_verdict == "accept" and overall_confidence >= 0.72:
                return "ready_for_downstream_extraction"
            return "review_borderline_case"

        if stable_topic_routing and stable_topic_routing.primary_topic and overall_confidence >= 0.72:
            return "ready_for_topic_routing"
        return "review_borderline_case"
