from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping, Sequence

from ._util import _assessment_weight
from .relevance import (
    ArticleCandidate,
    QuestionArticleRelevanceFilter,
    QuestionConstitution,
    RelevanceAssessment,
    SupportsArticleTypeClassification,
    SupportsRelevanceAdjudication,
)
from .registry_sink import SupportsClassificationRegistry


@dataclass(frozen=True)
class TopicBundleCandidate:
    topic: str
    score: float
    accepted_count: int
    edge_case_count: int
    topic_expansion_signal_count: int
    new_topic_signal_count: int
    max_novelty_signal: float
    best_question_id: str
    best_bundle_id: str
    best_verdict: str
    best_confidence: float
    proposed_topic_labels: tuple[str, ...] = ()
    assessments: tuple[RelevanceAssessment, ...] = ()


@dataclass(frozen=True)
class BundleRoutingResult:
    paper_id: str
    primary_topic: str | None
    primary_bundle_id: str | None
    candidates: tuple[TopicBundleCandidate, ...]
    emergent_candidates: tuple[TopicBundleCandidate, ...]
    all_assessments: tuple[RelevanceAssessment, ...]


class QuestionBundleRouter:
    """
    Reverse use of the relevance filter.

    Given one article and many constitutions, estimate which topic bundles the
    article most plausibly belongs to.
    """

    def __init__(
        self,
        constitutions: Sequence[QuestionConstitution],
        *,
        classifier: SupportsArticleTypeClassification | None = None,
        adjudicator: SupportsRelevanceAdjudication | None = None,
        registry_sink: SupportsClassificationRegistry | None = None,
        adjudication_policy: Literal["never", "borderline_only", "always"] = "borderline_only",
    ) -> None:
        self.constitutions = tuple(constitutions)
        self.registry_sink = registry_sink
        self._recorded_bundle_routing: set[str] = set()
        self.filter = QuestionArticleRelevanceFilter(
            classifier=classifier,
            adjudicator=adjudicator,
            registry_sink=registry_sink,
            adjudication_policy=adjudication_policy,
        )

    def route_article(self, article_like: ArticleCandidate | Mapping[str, Any]) -> BundleRoutingResult:
        article = article_like if isinstance(article_like, ArticleCandidate) else ArticleCandidate.from_mapping(article_like)
        assessments = [self.filter.assess(constitution, article) for constitution in self.constitutions]

        topic_groups: dict[str, list[RelevanceAssessment]] = {}
        for item in assessments:
            if item.verdict == "reject":
                continue
            topic = next(
                (
                    constitution.topic
                    for constitution in self.constitutions
                    if constitution.question_id == item.question_id
                ),
                "",
            ) or "untitled-topic"
            topic_groups.setdefault(topic, []).append(item)

        candidates: list[TopicBundleCandidate] = []
        for topic, items in topic_groups.items():
            accepted = [item for item in items if item.verdict == "accept"]
            edges = [item for item in items if item.verdict == "edge_case"]
            topic_expansion_items = [item for item in items if item.topic_expansion_candidate]
            new_topic_items = [item for item in items if item.new_topic_candidate]
            best = max(items, key=lambda item: (item.confidence, item.verdict == "accept"))
            score = round(sum(_assessment_weight(item) for item in items), 4)
            proposed_topic_labels = tuple(
                sorted({item.proposed_topic_label for item in items if item.proposed_topic_label})
            )
            candidates.append(
                TopicBundleCandidate(
                    topic=topic,
                    score=score,
                    accepted_count=len(accepted),
                    edge_case_count=len(edges),
                    topic_expansion_signal_count=len(topic_expansion_items),
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
        emergent_candidates = tuple(
            item for item in candidates
            if item.topic_expansion_signal_count > 0 or item.new_topic_signal_count > 0 or item.max_novelty_signal >= 0.65
        )
        result = BundleRoutingResult(
            paper_id=article.paper_id,
            primary_topic=primary.topic if primary else None,
            primary_bundle_id=primary.best_bundle_id if primary else None,
            candidates=tuple(candidates),
            emergent_candidates=emergent_candidates,
            all_assessments=tuple(sorted(assessments, key=lambda item: (-item.confidence, item.question_id))),
        )
        if self.registry_sink is not None and article.paper_id and article.paper_id not in self._recorded_bundle_routing:
            self.registry_sink.record_bundle_routing(article, result)
            self._recorded_bundle_routing.add(article.paper_id)
        return result
