from __future__ import annotations

from atlas_shared.bundle_router import QuestionBundleRouter
from atlas_shared.relevance import AdjudicationResult, ArticleCandidate, QuestionConstitution


class _NoveltyAdjudicator:
    def adjudicate(self, request):
        if "forest bathing" in request.article.title.lower():
            return AdjudicationResult(
                verdict="edge_case",
                confidence=0.79,
                reasons=("This looks like a broadening from attention into restoration and stress recovery.",),
                needs_manual_review=True,
                source="stub_llm",
                edge_case_kind="topic_expansion_candidate",
                novelty_signal=0.87,
                topic_expansion_candidate=True,
                new_topic_candidate=False,
                proposed_topic_label="Nature Exposure and Restoration",
                adjacent_topics=("Biophilia", "Affect"),
            )
        return None


class _RecordingSink:
    def __init__(self) -> None:
        self.routings = []

    def record_article_type(self, article, decision):
        return None

    def record_question_assessment(self, article, constitution, assessment):
        return None

    def record_question_summary(self, article, summary):
        return None

    def record_bundle_routing(self, article, routing):
        self.routings.append((article.paper_id, routing.primary_topic, routing.primary_bundle_id))


def test_router_prefers_topic_with_direct_accept_over_adjacent_edge_case() -> None:
    constitutions = [
        QuestionConstitution(
            question_id="Q1",
            question_text="Does daylight improve alertness?",
            topic="Lighting",
            environment_terms=("daylight", "window"),
            outcome_terms=("alertness", "fatigue"),
            exclusion_terms=("microscopy",),
            edge_terms=("mood",),
            required_evidence_terms=("participants", "p <", "experiment"),
        ),
        QuestionConstitution(
            question_id="Q2",
            question_text="Does nature exposure improve attention?",
            topic="Biophilia",
            environment_terms=("nature", "forest"),
            outcome_terms=("attention",),
            exclusion_terms=("adhd",),
            edge_terms=("restoration",),
            required_evidence_terms=("participants", "attention task"),
        ),
    ]

    router = QuestionBundleRouter(constitutions, adjudicator=_NoveltyAdjudicator())
    result = router.route_article(
        ArticleCandidate(
            paper_id="PDF-1001",
            title="Daylight improves alertness in office workers",
            abstract="We conducted an experiment with 62 participants and found greater alertness under daylight (p < .01).",
        )
    )

    assert result.primary_topic == "Lighting"
    assert result.primary_bundle_id == "bundle-lighting-q1"
    assert result.candidates[0].accepted_count == 1


def test_router_can_offer_secondary_topic_candidates() -> None:
    constitutions = [
        QuestionConstitution(
            question_id="Q1",
            question_text="Does forest exposure improve attention?",
            topic="Biophilia",
            environment_terms=("forest", "nature"),
            outcome_terms=("attention",),
            exclusion_terms=("adhd",),
            edge_terms=("restoration",),
            required_evidence_terms=("participants", "attention task"),
        ),
        QuestionConstitution(
            question_id="Q2",
            question_text="Does forest exposure reduce stress?",
            topic="Affect",
            environment_terms=("forest", "nature"),
            outcome_terms=("stress", "mood"),
            exclusion_terms=("adhd",),
            edge_terms=("restoration",),
            required_evidence_terms=("participants",),
        ),
    ]

    router = QuestionBundleRouter(constitutions, adjudicator=_NoveltyAdjudicator())
    result = router.route_article(
        {
            "paper_id": "PDF-1002",
            "title": "Forest bathing reduces stress in adults",
            "abstract": "Participants exposed to forest bathing showed lower stress and improved mood but no attention task was administered.",
        }
    )

    assert result.primary_topic == "Affect"
    assert len(result.candidates) >= 1
    assert any(candidate.topic == "Affect" for candidate in result.candidates)
    assert result.emergent_candidates
    assert result.emergent_candidates[0].max_novelty_signal == 0.87
    assert "Nature Exposure and Restoration" in result.emergent_candidates[0].proposed_topic_labels


def test_router_emits_single_bundle_routing_notification_per_paper() -> None:
    sink = _RecordingSink()
    constitutions = [
        QuestionConstitution(
            question_id="Q1",
            question_text="Does daylight improve alertness?",
            topic="Lighting",
            environment_terms=("daylight", "window"),
            outcome_terms=("alertness",),
        )
    ]

    router = QuestionBundleRouter(constitutions, registry_sink=sink)
    article = ArticleCandidate(
        paper_id="PDF-1003",
        title="Daylight improves alertness in office workers",
        abstract="Participants showed greater alertness under daylight.",
    )

    first = router.route_article(article)
    second = router.route_article(article)

    assert first.primary_topic == "Lighting"
    assert second.primary_topic == "Lighting"
    assert sink.routings == [("PDF-1003", "Lighting", "bundle-lighting-q1")]
