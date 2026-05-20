from __future__ import annotations

from atlas_shared.article_types import (
    HeuristicArticleTypeClassifier,
    article_type_signal_profile,
    build_article_type_surface,
)


def test_classifier_uses_later_paper_surface_not_only_front_slice() -> None:
    front_matter = " ".join(["copyright notice and image caption"] * 500)
    body = """
    # Introduction
    This paper examines architectural lighting in classrooms.

    # Methods
    Participants completed an experiment comparing daylight exposure conditions.
    The sample was N = 84 and the dependent variable was sustained attention.

    # Results
    ANOVA showed that daylight improved task accuracy, p < .01.
    """

    decision = HeuristicArticleTypeClassifier().classify(
        title="Lighting and attention",
        body_text=f"{front_matter}\n{body}",
    )

    assert decision.value == "empirical_research"
    assert decision.confidence > 0.5
    assert any("clean_chars=" in item for item in decision.evidence)


def test_surface_does_not_invent_empirical_type_from_empty_section_labels() -> None:
    text = """
    # Abstract
    This article reviews theories of workplace meaning and spatial identity.

    # Introduction
    We argue that buildings can organize social interpretation through a
    conceptual framework rather than through a new experiment.
    """

    surface = build_article_type_surface(text, title="A conceptual framework for workplace meaning")
    profile = article_type_signal_profile(text, title="A conceptual framework for workplace meaning", surface=surface)
    decision = HeuristicArticleTypeClassifier().classify(
        title="A conceptual framework for workplace meaning",
        body_text=text,
    )

    assert profile["families"]["empirical"]["hit_count"] == 0
    assert decision.value == "theoretical"


def test_signal_profile_records_negative_evidence_for_non_empirical_unknowns() -> None:
    text = """
    # Abstract
    A short essay on design language, interpretation, and practice.

    # Conclusion
    No experiment, participants, measures, or statistics are reported.
    """

    profile = article_type_signal_profile(text, title="Design language in practice")

    assert profile["families"]["empirical"]["negative_evidence"] is True
    assert profile["families"]["empirical"]["matched_patterns"] == []
