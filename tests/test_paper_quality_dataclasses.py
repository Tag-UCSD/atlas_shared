from __future__ import annotations

import json

from atlas_shared.paper_quality import (
    EffectSize,
    FingerprintField,
    HardRuleViolation,
    PaperQualityFingerprint,
    QualityFingerprintEnvelope,
    PowerRecord,
    PreregRecord,
    SourceExcerpt,
)


def _fingerprint() -> PaperQualityFingerprint:
    return PaperQualityFingerprint(
        paper_id="PDF-0001",
        extractor_version="synthetic-v1",
        extracted_at="2026-05-13T12:00:00Z",
        human_adjudicated=True,
        adjudicator_id="dk",
        adjudicated_at="2026-05-13T13:00:00Z",
        n_total=FingerprintField(
            value=128,
            confidence=0.93,
            logprob_proxy=0.88,
            source_excerpt=SourceExcerpt(page=4, paragraph=2, quoted_span="N = 128"),
        ),
        sample_country=FingerprintField(value=("US", "CA")),
        sample_setting=FingerprintField(value="research_university"),
        sample_weird=FingerprintField(value=True),
        age_distribution_json=FingerprintField(value={"mean": 21.4, "sd": 3.1}),
        design_type=FingerprintField(value="lab_experiment"),
        preregistration=FingerprintField(
            value=PreregRecord(
                url="https://osf.io/example",
                timestamp="2024-01-01T00:00:00Z",
                hypothesis_text="Nature views improve restoration.",
                registry_kind="osf",
                verified=True,
            )
        ),
        replication_count=FingerprintField(value=2),
        primary_effect_size=FingerprintField(
            value=EffectSize(
                value=0.42,
                metric="d",
                ci_lower=0.20,
                ci_upper=0.64,
                computed_or_reported="reported",
                origin="reported",
            )
        ),
        statistical_power=FingerprintField(
            value=PowerRecord(value=0.81, origin="a_priori_reported")
        ),
        primary_measure=FingerprintField(value="restoration scale"),
        primary_measure_psychometric_ref=FingerprintField(value="PRS"),
        open_data_url=FingerprintField(value="https://osf.io/data"),
        open_data_verified=FingerprintField(value=True),
        construct_validity_flag="good",
        construct_validity_notes="Validated scale.",
        conflict_of_interest_severity="none",
        rhetorical_flags_json=("overclaiming_absent",),
        field_norms_version="norms-v1",
        overall_confidence=0.91,
        notes_markdown="Synthetic fixture.",
    )


def test_fingerprint_round_trips_through_json_without_field_loss() -> None:
    original = _fingerprint()
    encoded = json.loads(json.dumps(original.to_json_dict()))
    recovered = PaperQualityFingerprint.from_json_dict(encoded)

    assert recovered.paper_id == original.paper_id
    assert recovered.n_total.value == 128
    assert recovered.n_total.source_excerpt.page == 4
    assert recovered.sample_country.value == ("US", "CA")
    assert recovered.preregistration.value.url == "https://osf.io/example"
    assert recovered.primary_effect_size.value.ci_upper == 0.64
    assert recovered.statistical_power.value.origin == "a_priori_reported"
    assert recovered.rhetorical_flags_json == ("overclaiming_absent",)


def test_fingerprint_round_trips_through_sql_shape_without_field_loss() -> None:
    original = _fingerprint()
    sql_row = original.to_sql_row()
    recovered = PaperQualityFingerprint.from_sql_row(sql_row)

    assert recovered.paper_id == original.paper_id
    assert recovered.extractor_version == "synthetic-v1"
    assert recovered.n_total.value == 128
    assert recovered.n_total.confidence == 0.93
    assert recovered.sample_country.value == ("US", "CA")
    assert recovered.sample_setting.value == "research_university"
    assert recovered.sample_weird.value is True
    assert recovered.age_distribution_json.value == {"mean": 21.4, "sd": 3.1}
    assert recovered.design_type.value == "lab_experiment"
    assert recovered.preregistration.value.verified is True
    assert recovered.replication_count.value == 2
    assert recovered.primary_effect_size.value.value == 0.42
    assert recovered.primary_effect_size.value.metric == "d"
    assert recovered.statistical_power.value.value == 0.81
    assert recovered.primary_measure.value == "restoration scale"
    assert recovered.open_data_verified.value is True
    assert recovered.construct_validity_flag == "good"
    assert recovered.conflict_of_interest_severity == "none"


def test_hard_rule_violation_round_trips_through_sql_shape() -> None:
    original = HardRuleViolation(
        paper_id="PDF-0001",
        rule_id="HARD_RULE_9",
        field_name="n_total",
        violation_state={"assertion": "missing quoted span"},
        violation_timestamp="2026-05-13T12:00:00Z",
    )

    recovered = HardRuleViolation.from_sql_row(original.to_sql_row())

    assert recovered.paper_id == original.paper_id
    assert recovered.rule_id == "HARD_RULE_9"
    assert recovered.field_name == "n_total"
    assert recovered.violation_state == {"assertion": "missing quoted span"}
    assert recovered.requires_dk_review is True


def test_pydantic_schema_wraps_fingerprint_payload() -> None:
    schema = QualityFingerprintEnvelope.from_fingerprint(_fingerprint())

    assert schema.paper_id == "PDF-0001"
    assert schema.extractor_version == "synthetic-v1"
    assert schema.fingerprint["n_total"]["value"] == 128


def test_fingerprint_normalizes_bel_prefixed_identifier_and_records_short_circuit() -> None:
    fingerprint = PaperQualityFingerprint(
        paper_id="bel_PDF-0042",
        extractor_version="synthetic-v1",
        attached_via_short_circuit=True,
    )

    assert fingerprint.paper_id == "PDF-0042"
    assert fingerprint.attached_via_short_circuit is True
    assert fingerprint.to_json_dict()["attached_via_short_circuit"] is True
    assert fingerprint.to_sql_row()["paper_id"] == "PDF-0042"


def test_hard_rule_violation_normalizes_bel_prefixed_identifier() -> None:
    violation = HardRuleViolation(
        paper_id="bel_PDF-0042",
        rule_id="HARD_RULE_8",
        field_name="sample_country",
        violation_state={"reason": "synthetic"},
    )

    assert violation.paper_id == "PDF-0042"
    assert violation.to_sql_row()["paper_id"] == "PDF-0042"
