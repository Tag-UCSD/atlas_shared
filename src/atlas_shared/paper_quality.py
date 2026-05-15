from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
import json
from typing import Any, Generic, Literal, Mapping, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")

WEIGHTING_FUNCTION_VERSION = "v1.0-2026-05-13"

SampleSetting = Literal[
    "research_university",
    "community",
    "online_panel",
    "industrial",
    "clinical",
    "mixed",
    "other",
]
DesignType = Literal[
    "lab_experiment",
    "field_experiment",
    "observational_cohort",
    "online",
    "secondary_analysis",
    "meta_analysis",
    "theoretical",
]
RegistryKind = Literal["osf", "aspredicted", "clinicaltrials_gov", "journal_rr", "unknown"]
EffectMetric = Literal["d", "r", "or", "hr", "bayes_factor"]
EffectOrigin = Literal[
    "reported",
    "computed_from_t_and_n",
    "computed_from_chi_square",
    "computed_from_f",
    "computed_from_p_and_n",
    "unknown",
]
PowerOrigin = Literal["a_priori_reported", "retrospective_computed", "not_reported"]
ConstructValidityFlag = Literal["good", "questionable", "mixed", "not_assessed"]
ConflictSeverity = Literal["none", "minor", "moderate", "severe", "unknown"]


@dataclass(frozen=True)
class SourceExcerpt:
    page: int | None = None
    paragraph: int | None = None
    quoted_span: str = ""

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any] | None) -> "SourceExcerpt":
        if not obj:
            return cls()
        return cls(
            page=_optional_int(obj.get("page")),
            paragraph=_optional_int(obj.get("paragraph")),
            quoted_span=str(obj.get("quoted_span") or ""),
        )


@dataclass(frozen=True)
class FingerprintField(Generic[T]):
    value: T | None = None
    confidence: float | None = None
    logprob_proxy: float | None = None
    per_element_agreement: Mapping[str, float] = field(default_factory=dict)
    source_excerpt: SourceExcerpt = field(default_factory=SourceExcerpt)
    weighting_function_version: str = WEIGHTING_FUNCTION_VERSION

    @classmethod
    def from_mapping(cls, obj: Mapping[str, Any] | None) -> "FingerprintField[Any]":
        if not obj:
            return cls()
        return cls(
            value=obj.get("value"),
            confidence=_optional_float(obj.get("confidence")),
            logprob_proxy=_optional_float(obj.get("logprob_proxy")),
            per_element_agreement=dict(obj.get("per_element_agreement") or {}),
            source_excerpt=SourceExcerpt.from_mapping(obj.get("source_excerpt")),
            weighting_function_version=str(
                obj.get("weighting_function_version") or WEIGHTING_FUNCTION_VERSION
            ),
        )


@dataclass(frozen=True)
class PreregRecord:
    url: str = ""
    timestamp: str = ""
    hypothesis_text: str = ""
    registry_kind: RegistryKind = "unknown"
    verified: bool = False


@dataclass(frozen=True)
class EffectSize:
    value: float | None = None
    metric: EffectMetric | None = None
    ci_lower: float | None = None
    ci_upper: float | None = None
    computed_or_reported: Literal["computed", "reported", "unknown"] = "unknown"
    origin: EffectOrigin = "unknown"

    @property
    def ci_width(self) -> float | None:
        if self.ci_lower is None or self.ci_upper is None:
            return None
        return self.ci_upper - self.ci_lower


@dataclass(frozen=True)
class PowerRecord:
    value: float | None = None
    origin: PowerOrigin = "not_reported"
    hoenig_heisey_caveat: bool = False


@dataclass(frozen=True)
class HardRuleViolation:
    paper_id: str
    rule_id: Literal["HARD_RULE_7", "HARD_RULE_8", "HARD_RULE_9"]
    field_name: str | None
    violation_state: Mapping[str, Any]
    violation_timestamp: str = ""
    requires_dk_review: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "paper_id", normalize_paper_id(self.paper_id))

    def to_sql_row(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "rule_id": self.rule_id,
            "field_name": self.field_name,
            "violation_state": json.dumps(self.violation_state, sort_keys=True),
            "violation_timestamp": self.violation_timestamp,
            "requires_dk_review": int(self.requires_dk_review),
        }

    @classmethod
    def from_sql_row(cls, row: Mapping[str, Any]) -> "HardRuleViolation":
        return cls(
            paper_id=str(row["paper_id"]),
            rule_id=row["rule_id"],
            field_name=row.get("field_name"),
            violation_state=_json_obj(row.get("violation_state"), {}),
            violation_timestamp=str(row.get("violation_timestamp") or ""),
            requires_dk_review=bool(row.get("requires_dk_review", 1)),
        )


@dataclass(frozen=True)
class PaperQualityFingerprint:
    paper_id: str
    extractor_version: str
    attached_via_short_circuit: bool = False
    extracted_at: str = ""
    human_adjudicated: bool = False
    adjudicator_id: str | None = None
    adjudicated_at: str | None = None
    n_total: FingerprintField[int] = field(default_factory=FingerprintField)
    sample_country: FingerprintField[tuple[str, ...]] = field(default_factory=FingerprintField)
    sample_setting: FingerprintField[SampleSetting] = field(default_factory=FingerprintField)
    sample_weird: FingerprintField[bool] = field(default_factory=FingerprintField)
    age_distribution_json: FingerprintField[Mapping[str, Any]] = field(default_factory=FingerprintField)
    design_type: FingerprintField[DesignType] = field(default_factory=FingerprintField)
    preregistration: FingerprintField[PreregRecord] = field(default_factory=FingerprintField)
    replication_count: FingerprintField[int] = field(default_factory=FingerprintField)
    primary_effect_size: FingerprintField[EffectSize] = field(default_factory=FingerprintField)
    statistical_power: FingerprintField[PowerRecord] = field(default_factory=FingerprintField)
    primary_measure: FingerprintField[str] = field(default_factory=FingerprintField)
    primary_measure_psychometric_ref: FingerprintField[str] = field(default_factory=FingerprintField)
    open_data_url: FingerprintField[str] = field(default_factory=FingerprintField)
    open_data_verified: FingerprintField[bool] = field(default_factory=FingerprintField)
    construct_validity_flag: ConstructValidityFlag | None = None
    construct_validity_notes: str | None = None
    conflict_of_interest_severity: ConflictSeverity | None = None
    rhetorical_flags_json: tuple[str, ...] = ()
    field_norms_version: str | None = None
    overall_confidence: float | None = None
    notes_markdown: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "paper_id", normalize_paper_id(self.paper_id))

    def to_json_dict(self) -> dict[str, Any]:
        return _to_jsonable(asdict(self))

    @classmethod
    def from_json_dict(cls, obj: Mapping[str, Any]) -> "PaperQualityFingerprint":
        kwargs: dict[str, Any] = {
            "paper_id": str(obj["paper_id"]),
            "extractor_version": str(obj["extractor_version"]),
            "attached_via_short_circuit": bool(obj.get("attached_via_short_circuit", False)),
            "extracted_at": str(obj.get("extracted_at") or ""),
            "human_adjudicated": bool(obj.get("human_adjudicated", False)),
            "adjudicator_id": obj.get("adjudicator_id"),
            "adjudicated_at": obj.get("adjudicated_at"),
            "construct_validity_flag": obj.get("construct_validity_flag"),
            "construct_validity_notes": obj.get("construct_validity_notes"),
            "conflict_of_interest_severity": obj.get("conflict_of_interest_severity"),
            "rhetorical_flags_json": tuple(obj.get("rhetorical_flags_json") or ()),
            "field_norms_version": obj.get("field_norms_version"),
            "overall_confidence": _optional_float(obj.get("overall_confidence")),
            "notes_markdown": obj.get("notes_markdown"),
            "created_at": str(obj.get("created_at") or ""),
            "updated_at": str(obj.get("updated_at") or ""),
        }
        for name in _FINGERPRINT_FIELD_NAMES:
            kwargs[name] = FingerprintField.from_mapping(obj.get(name))
        kwargs["sample_country"] = _field_tuple(kwargs["sample_country"])
        kwargs["preregistration"] = _field_dataclass(kwargs["preregistration"], PreregRecord)
        kwargs["primary_effect_size"] = _field_dataclass(kwargs["primary_effect_size"], EffectSize)
        kwargs["statistical_power"] = _field_dataclass(kwargs["statistical_power"], PowerRecord)
        return cls(**kwargs)

    def to_sql_row(self) -> dict[str, Any]:
        prereg = self.preregistration.value or PreregRecord()
        effect = self.primary_effect_size.value or EffectSize()
        power = self.statistical_power.value or PowerRecord()
        return {
            "paper_id": self.paper_id,
            "extracted_at": self.extracted_at,
            "extractor_version": self.extractor_version,
            "human_adjudicated": int(self.human_adjudicated),
            "adjudicator_id": self.adjudicator_id,
            "adjudicated_at": self.adjudicated_at,
            "n_total": self.n_total.value,
            "n_total_confidence": self.n_total.confidence,
            "sample_country": json.dumps(list(self.sample_country.value or ())),
            "sample_setting": self.sample_setting.value,
            "sample_weird": _optional_bool_int(self.sample_weird.value),
            "age_distribution_json": json.dumps(self.age_distribution_json.value or {}),
            "design_type": self.design_type.value,
            "preregistered": _optional_bool_int(bool(prereg.url or prereg.hypothesis_text) or None),
            "preregistration_url": prereg.url or None,
            "preregistration_verified": _optional_bool_int(prereg.verified),
            "preregistration_verified_at": prereg.timestamp or None,
            "replication_count": self.replication_count.value,
            "primary_effect_size": effect.value,
            "primary_ci_lower": effect.ci_lower,
            "primary_ci_upper": effect.ci_upper,
            "primary_metric": effect.metric,
            "statistical_power": power.value,
            "power_origin": power.origin,
            "primary_measure": self.primary_measure.value,
            "primary_measure_psychometric_ref": self.primary_measure_psychometric_ref.value,
            "open_data_url": self.open_data_url.value,
            "open_data_verified": _optional_bool_int(self.open_data_verified.value),
            "construct_validity_flag": self.construct_validity_flag,
            "construct_validity_notes": self.construct_validity_notes,
            "conflict_of_interest_severity": self.conflict_of_interest_severity,
            "rhetorical_flags_json": json.dumps(list(self.rhetorical_flags_json)),
            "field_norms_version": self.field_norms_version,
            "overall_confidence": self.overall_confidence,
            "notes_markdown": self.notes_markdown,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_sql_row(cls, row: Mapping[str, Any]) -> "PaperQualityFingerprint":
        prereg = PreregRecord(
            url=str(row.get("preregistration_url") or ""),
            timestamp=str(row.get("preregistration_verified_at") or ""),
            registry_kind="unknown",
            verified=bool(row.get("preregistration_verified") or False),
        )
        effect = EffectSize(
            value=_optional_float(row.get("primary_effect_size")),
            metric=row.get("primary_metric"),
            ci_lower=_optional_float(row.get("primary_ci_lower")),
            ci_upper=_optional_float(row.get("primary_ci_upper")),
            computed_or_reported="unknown",
            origin="unknown",
        )
        power = PowerRecord(
            value=_optional_float(row.get("statistical_power")),
            origin=row.get("power_origin") or "not_reported",
            hoenig_heisey_caveat=row.get("power_origin") == "retrospective_computed",
        )
        return cls(
            paper_id=str(row["paper_id"]),
            extracted_at=str(row.get("extracted_at") or ""),
            extractor_version=str(row["extractor_version"]),
            attached_via_short_circuit=bool(row.get("attached_via_short_circuit", False)),
            human_adjudicated=bool(row.get("human_adjudicated") or False),
            adjudicator_id=row.get("adjudicator_id"),
            adjudicated_at=row.get("adjudicated_at"),
            n_total=FingerprintField(
                value=_optional_int(row.get("n_total")),
                confidence=_optional_float(row.get("n_total_confidence")),
            ),
            sample_country=FingerprintField(value=tuple(_json_obj(row.get("sample_country"), []))),
            sample_setting=FingerprintField(value=row.get("sample_setting")),
            sample_weird=FingerprintField(value=_optional_bool(row.get("sample_weird"))),
            age_distribution_json=FingerprintField(value=_json_obj(row.get("age_distribution_json"), {})),
            design_type=FingerprintField(value=row.get("design_type")),
            preregistration=FingerprintField(value=prereg),
            replication_count=FingerprintField(value=_optional_int(row.get("replication_count"))),
            primary_effect_size=FingerprintField(value=effect),
            statistical_power=FingerprintField(value=power),
            primary_measure=FingerprintField(value=row.get("primary_measure")),
            primary_measure_psychometric_ref=FingerprintField(
                value=row.get("primary_measure_psychometric_ref")
            ),
            open_data_url=FingerprintField(value=row.get("open_data_url")),
            open_data_verified=FingerprintField(value=_optional_bool(row.get("open_data_verified"))),
            construct_validity_flag=row.get("construct_validity_flag"),
            construct_validity_notes=row.get("construct_validity_notes"),
            conflict_of_interest_severity=row.get("conflict_of_interest_severity"),
            rhetorical_flags_json=tuple(_json_obj(row.get("rhetorical_flags_json"), [])),
            field_norms_version=row.get("field_norms_version"),
            overall_confidence=_optional_float(row.get("overall_confidence")),
            notes_markdown=row.get("notes_markdown"),
            created_at=str(row.get("created_at") or ""),
            updated_at=str(row.get("updated_at") or ""),
        )


class QualityFingerprintEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    paper_id: str
    extractor_version: str
    fingerprint: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_fingerprint(cls, fingerprint: PaperQualityFingerprint) -> "QualityFingerprintEnvelope":
        return cls(
            paper_id=fingerprint.paper_id,
            extractor_version=fingerprint.extractor_version,
            fingerprint=fingerprint.to_json_dict(),
        )


@dataclass(frozen=True)
class SampleOverlapEdge:
    paper_id_a: str
    paper_id_b: str
    overlap_kind: Literal["shared_dataset", "shared_authors", "shared_subjects", "meta_of_meta"]
    confidence: float
    detected_by: Literal["author_id", "dataset_doi", "manual", "llm"]

    def __post_init__(self) -> None:
        object.__setattr__(self, "paper_id_a", normalize_paper_id(self.paper_id_a))
        object.__setattr__(self, "paper_id_b", normalize_paper_id(self.paper_id_b))


_FINGERPRINT_FIELD_NAMES = tuple(
    f.name
    for f in fields(PaperQualityFingerprint)
    if f.name
    in {
        "n_total",
        "sample_country",
        "sample_setting",
        "sample_weird",
        "age_distribution_json",
        "design_type",
        "preregistration",
        "replication_count",
        "primary_effect_size",
        "statistical_power",
        "primary_measure",
        "primary_measure_psychometric_ref",
        "open_data_url",
        "open_data_verified",
    }
)


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    return value


def normalize_paper_id(paper_id: str) -> str:
    value = str(paper_id or "").strip()
    if value.startswith("bel_PDF-"):
        return value[4:]
    return value


def _json_obj(value: Any, default: Any) -> Any:
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list, tuple)):
        return value
    try:
        return json.loads(str(value))
    except json.JSONDecodeError:
        return default


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _optional_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    return bool(value)


def _optional_bool_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(bool(value))


def _field_tuple(value: FingerprintField[Any]) -> FingerprintField[tuple[Any, ...]]:
    return FingerprintField(
        value=tuple(value.value or ()),
        confidence=value.confidence,
        logprob_proxy=value.logprob_proxy,
        per_element_agreement=value.per_element_agreement,
        source_excerpt=value.source_excerpt,
        weighting_function_version=value.weighting_function_version,
    )


def _field_dataclass(value: FingerprintField[Any], cls: type[T]) -> FingerprintField[T]:
    raw = value.value
    parsed = cls(**raw) if isinstance(raw, Mapping) else raw
    return FingerprintField(
        value=parsed,
        confidence=value.confidence,
        logprob_proxy=value.logprob_proxy,
        per_element_agreement=value.per_element_agreement,
        source_excerpt=value.source_excerpt,
        weighting_function_version=value.weighting_function_version,
    )
