from __future__ import annotations

from atlas_shared.relevance import (
    AdjudicationResult,
    ArticleCandidate,
    QuestionArticleRelevanceFilter,
    QuestionConstitution,
)


class _RecordingSink:
    def __init__(self) -> None:
        self.article_types = []
        self.assessments = []

    def record_article_type(self, article, decision):
        self.article_types.append((article.paper_id, decision.value))

    def record_question_assessment(self, article, constitution, assessment):
        self.assessments.append((article.paper_id, constitution.question_id, assessment.verdict))

    def record_question_summary(self, article, summary):
        raise AssertionError("Question summary should not be recorded from the shared filter directly")

    def record_bundle_routing(self, article, routing):
        raise AssertionError("Bundle routing should not be recorded from the shared filter directly")


def _constitution() -> QuestionConstitution:
    return QuestionConstitution(
        question_id="SQ-ART-001",
        question_text="Does exposure to natural environments improve directed attention in adults?",
        topic="Nature and Attention",
        environment_terms=("nature", "green space", "natural environment", "forest", "biophilic"),
        outcome_terms=("directed attention", "attention", "executive attention", "cognitive restoration"),
        exclusion_terms=("adhd", "attention deficit", "attention disorder"),
        edge_terms=("stress recovery", "restoration", "mood"),
        search_hints=("green view", "attention task"),
        required_evidence_terms=("participants", "p <", "sample", "experiment"),
    )


def test_relevance_filter_accepts_clear_empirical_match() -> None:
    filt = QuestionArticleRelevanceFilter()
    constitution = _constitution()
    article = ArticleCandidate(
        paper_id="PDF-0001",
        title="Natural environments improve directed attention in office workers",
        abstract=(
            "We conducted an experiment with 84 participants to test whether a green view improves "
            "directed attention. Results showed significant gains in attention task performance (p < .01)."
        ),
    )

    result = filt.assess(constitution, article)

    assert result.article_type.value == "empirical_research"
    assert result.verdict == "accept"
    assert result.needs_manual_review is False
    assert result.environment_hits
    assert "directed attention" in result.outcome_hits


def test_relevance_filter_rejects_false_friend_attention_deficit_case() -> None:
    filt = QuestionArticleRelevanceFilter()
    constitution = _constitution()
    article = ArticleCandidate(
        paper_id="PDF-0002",
        title="Natural classroom interventions for children with ADHD",
        abstract="This study examines attention deficit symptoms in children with ADHD following outdoor activity.",
    )

    result = filt.assess(constitution, article)

    assert result.verdict == "reject"
    assert result.exclusion_hits


def test_relevance_filter_marks_partial_overlap_as_edge_case() -> None:
    filt = QuestionArticleRelevanceFilter()
    constitution = _constitution()
    article = ArticleCandidate(
        paper_id="PDF-0003",
        title="Forest bathing reduces stress in adults",
        abstract=(
            "Participants exposed to forest bathing showed lower cortisol and improved mood, "
            "but no attention task was administered."
        ),
    )

    result = filt.assess(constitution, article)

    assert result.verdict == "edge_case"
    assert result.needs_manual_review is True
    assert result.environment_hits
    assert not result.outcome_hits or "attention" not in result.outcome_hits


def test_build_article_bundle_sorts_accepts_and_edge_cases() -> None:
    filt = QuestionArticleRelevanceFilter()
    constitution = _constitution()
    bundle = filt.build_article_bundle(
        constitution,
        [
            {
                "paper_id": "PDF-0001",
                "title": "Natural environments improve directed attention in office workers",
                "abstract": "We conducted an experiment with 84 participants; attention improved (p < .01).",
            },
            {
                "paper_id": "PDF-0003",
                "title": "Forest bathing reduces stress in adults",
                "abstract": "Forest exposure reduced stress and improved mood, but no attention task was administered.",
            },
            {
                "paper_id": "PDF-0002",
                "title": "Natural classroom interventions for children with ADHD",
                "abstract": "Attention deficit symptoms improved after outdoor activity.",
            },
        ],
    )

    assert bundle.bundle_id == "bundle-nature-and-attention-sq-art-001"
    assert [item.paper_id for item in bundle.accepted] == ["PDF-0001"]
    assert [item.paper_id for item in bundle.edge_cases] == ["PDF-0003"]
    assert [item.paper_id for item in bundle.rejected] == ["PDF-0002"]


def test_bundle_id_disambiguates_constitutions_that_share_a_topic() -> None:
    first = QuestionConstitution(
        question_id="Q-LIGHT-ATTN",
        question_text="Does lighting improve attention?",
        topic="Lighting",
    )
    second = QuestionConstitution(
        question_id="Q-LIGHT-MOOD",
        question_text="Does lighting improve mood?",
        topic="Lighting",
    )

    assert first.bundle_id == "bundle-lighting-q-light-attn"
    assert second.bundle_id == "bundle-lighting-q-light-mood"
    assert first.bundle_id != second.bundle_id


def test_bundle_id_remains_stably_derived_from_topic_for_single_question() -> None:
    constitution = _constitution()

    assert constitution.bundle_id == "bundle-nature-and-attention-sq-art-001"
    assert constitution.bundle_id.startswith("bundle-nature-and-attention")


class _StubAdjudicator:
    def adjudicate(self, request):
        return AdjudicationResult(
            verdict="accept",
            confidence=0.83,
            reasons=("LLM panel judged the restoration framing close enough to remain in-bounds.",),
            needs_manual_review=False,
            source="stub_llm",
            edge_case_kind="topic_expansion_candidate",
            novelty_signal=0.81,
            topic_expansion_candidate=True,
            new_topic_candidate=False,
            proposed_topic_label="Nature Exposure and Restoration",
            adjacent_topics=("Nature and Attention", "Affect Regulation"),
        )


def test_borderline_case_can_be_promoted_by_adjudicator() -> None:
    filt = QuestionArticleRelevanceFilter(adjudicator=_StubAdjudicator())
    constitution = _constitution()
    article = ArticleCandidate(
        paper_id="PDF-0004",
        title="Forest bathing reduces stress in adults",
        abstract="Forest exposure reduced stress and improved mood, but no attention task was administered.",
    )

    result = filt.assess(constitution, article)

    assert result.verdict == "accept"
    assert result.adjudication_source == "stub_llm"
    assert result.edge_case_kind == "topic_expansion_candidate"
    assert result.topic_expansion_candidate is True
    assert result.novelty_signal == 0.81
    assert result.proposed_topic_label == "Nature Exposure and Restoration"
    assert any("LLM panel judged" in reason for reason in result.reasons)


def test_relevance_filter_emits_registry_notifications_once_per_paper_question() -> None:
    sink = _RecordingSink()
    filt = QuestionArticleRelevanceFilter(registry_sink=sink)
    constitution = _constitution()
    article = ArticleCandidate(
        paper_id="PDF-0099",
        title="Natural environments improve directed attention in office workers",
        abstract=(
            "We conducted an experiment with 84 participants to test whether a green view improves "
            "directed attention. Results showed significant gains in attention task performance (p < .01)."
        ),
    )

    first = filt.assess(constitution, article)
    second = filt.assess(constitution, article)

    assert first.verdict == "accept"
    assert second.verdict == "accept"
    assert sink.article_types == [("PDF-0099", "empirical_research")]
    assert sink.assessments == [("PDF-0099", "SQ-ART-001", "accept")]
