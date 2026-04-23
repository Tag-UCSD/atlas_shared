from __future__ import annotations

from atlas_shared.intake import PreExtractionArticleIntake, PreExtractionIntakeGate
from atlas_shared.relevance import QuestionConstitution


def _constitutions() -> tuple[QuestionConstitution, ...]:
    return (
        QuestionConstitution(
            question_id="Q-LIGHT",
            question_text="Does daylight improve alertness in workplaces?",
            topic="Lighting",
            environment_terms=("daylight", "window", "lighting"),
            outcome_terms=("alertness", "fatigue"),
            exclusion_terms=("microscopy",),
            required_evidence_terms=("participants", "experiment", "p <"),
        ),
        QuestionConstitution(
            question_id="Q-NATURE",
            question_text="Does nature exposure improve attention?",
            topic="Biophilia",
            environment_terms=("nature", "forest", "green space"),
            outcome_terms=("attention", "cognitive restoration"),
            exclusion_terms=("adhd",),
            edge_terms=("restoration", "stress"),
        ),
    )


def test_intake_accepts_clear_topic_match_and_emits_facts() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        PreExtractionArticleIntake(
            paper_id="PDF-2001",
            title="Daylight improves alertness in office workers",
            abstract=(
                "An experiment with 72 participants found that daylight exposure "
                "improved alertness and reduced fatigue in office workstations (p < .01)."
            ),
        )
    )

    assert result.intake_decision == "accept_candidate"
    assert result.routing_target == "article_eater"
    assert result.primary_topic == "Lighting"
    assert result.needs_manual_review is False
    assert result.matched_question_ids == ("Q-LIGHT",)
    assert {fact.dimension for fact in result.facts} >= {
        "article_type_preliminary",
        "pre_extraction_intake_decision",
        "topic_routing_preliminary",
    }


def test_intake_preserves_plausible_new_topic_instead_of_rejecting() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2002",
            "title": "Scent gradients and wayfinding trust in hospital corridors",
            "abstract": (
                "Participants navigated a hospital corridor simulation with varied scent gradients. "
                "The study measured spatial decisions, preference, and trust in wayfinding cues."
            ),
            "keywords": ["scented wayfinding", "hospital design"],
        }
    )

    assert result.intake_decision == "edge_case"
    assert result.routing_target == "manual_review"
    assert result.new_topic_candidate is True
    assert result.topic_expansion_candidate is False
    assert result.proposed_topic_label == "scented wayfinding"
    assert result.domain_relevance == "adjacent_or_novel"
    assert "reject" not in result.intake_decision
    assert any(fact.dimension == "novelty_preservation" for fact in result.facts)


def test_intake_holds_title_only_record_for_more_text() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2003",
            "title": "Daylight and alertness in offices",
        }
    )

    assert result.intake_decision == "needs_pdf_text"
    assert result.routing_target == "hold_for_metadata"
    assert result.needs_manual_review is True


def test_intake_can_use_post_extraction_json_fields_without_abstract() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2003B",
            "processing_stage": "post_extraction",
            "title": "Lighting and fatigue in office work",
            "methods_surface_summary": "Participants completed an office lighting experiment with p < .05.",
            "independent_variables": "daylight exposure, window access",
            "dependent_variables": "alertness, fatigue",
            "measurement_inventory": [
                {
                    "outcome": "alertness",
                    "measure_name": "alertness rating",
                    "instrument_name": "self report scale",
                }
            ],
        }
    )

    assert result.intake_decision == "accept_candidate"
    assert result.routing_target == "article_eater"
    assert result.primary_topic == "Lighting"
    assert result.facts[0].details_json["processing_stage"] == "post_extraction"
    assert "measurement_terms" in result.facts[0].details_json["available_evidence_types"]


def test_intake_rejects_clear_false_positive_only_without_domain_signal() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2004",
            "title": "Plasma turbulence in galactic molecular clouds",
            "abstract": (
                "This astrophysics article models plasma turbulence and molecular dynamics "
                "in galactic clouds using computational simulation."
            ),
        }
    )

    assert result.intake_decision == "reject_clear_false_positive"
    assert result.routing_target == "reject"
    assert result.domain_relevance == "clear_false_positive"
    assert result.needs_manual_review is False


def test_intake_keeps_false_positive_terms_when_domain_signal_exists() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2005",
            "title": "Molecular lighting metaphors in hospital wayfinding design",
            "abstract": (
                "Participants evaluated hospital wayfinding signs and lighting metaphors "
                "for preference and spatial decision confidence."
            ),
        }
    )

    assert result.intake_decision == "edge_case"
    assert result.routing_target == "manual_review"
    assert result.domain_relevance == "adjacent_or_novel"
    assert result.topic_expansion_candidate is True
    assert result.proposed_topic_label


def test_intake_hard_rejects_clear_false_positive_particle_physics() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2006",
            "title": "Particle physics and galactic turbulence",
            "abstract": "This paper models particle physics interactions in galactic systems.",
        }
    )

    assert result.intake_decision == "reject_clear_false_positive"
    assert result.routing_target == "reject"
    assert result.needs_manual_review is False


def test_intake_soft_false_positive_enzyme_stress_goes_to_manual_review() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2007",
            "title": "Cortisol enzyme markers and workplace stress",
            "abstract": (
                "This paper examines cortisol enzyme markers, perceived workplace stress, "
                "and office fatigue in employees."
            ),
        }
    )

    assert result.intake_decision == "manual_review"
    assert result.routing_target == "manual_review"
    assert result.needs_manual_review is True
    assert result.domain_relevance == "adjacent_or_novel"


def test_intake_no_false_positive_terms_passes_without_keyword_rejection() -> None:
    gate = PreExtractionIntakeGate(_constitutions())
    result = gate.assess(
        {
            "paper_id": "PDF-2008",
            "title": "Window access improves alertness in office work",
            "abstract": (
                "An experiment with 44 participants found that window access improved "
                "alertness and reduced fatigue in workplaces (p < .05)."
            ),
        }
    )

    assert result.intake_decision == "accept_candidate"
    assert result.routing_target == "article_eater"
