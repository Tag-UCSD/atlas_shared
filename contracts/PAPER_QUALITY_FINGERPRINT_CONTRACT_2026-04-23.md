# Paper-Quality Fingerprint Contract

Date: 2026-04-23

Canonical implementation:

`atlas_shared.paper_quality.PaperQualityFingerprint`

## Scope

The paper-quality fingerprint is the shared type contract for quality metadata
about a single paper. It mirrors the Knowledge Atlas
`paper_quality_fingerprints` table while preserving extraction provenance,
confidence, and field-level warrant metadata in Python.

## Inputs

Inputs are structured extraction outputs from the paper-quality extractor and
human adjudication sidecars. Extractable fields must be represented as
`FingerprintField[T]` values carrying confidence, source excerpt, agreement
metadata, and the weighting-function version active at extraction time.

`paper_id` is the raw lifecycle identifier, for example `PDF-0042`, not a
belief-reference identifier such as `bel_PDF-0042`. The canonical dataclass
normalizes `bel_PDF-*` inputs before persistence. If admission is resolved via
the pre-admission dedup short circuit, the fingerprint records
`attached_via_short_circuit=True` while retaining the existing raw `paper_id`.

## Outputs

The module must support:

- JSON round-tripping for fingerprints and nested field records.
- SQL-row round-tripping for the `paper_quality_fingerprints` table.
- SQL-row round-tripping for `hard_rule_violations`.
- Pydantic validation via `QualityFingerprintEnvelope`.

## Success Conditions

A consumer must be able to serialize a fingerprint, deserialize it, write it to
the Knowledge Atlas SQL shape, and recover the semantic fields without losing
paper ID, extractor version, sample descriptors, design descriptors, effect
size, power, preregistration, openness, short-circuit attachment state, or
human-review sidecars.

## Non-Promises

This contract does not perform extraction, adjudication, calibration, database
writes, LLM calls, or claim-level aggregation. Those belong to repo-specific
orchestration layers and later pipeline passes.

## Test Coverage

`tests/test_paper_quality_dataclasses.py` covers JSON round-trips, SQL-row
round-trips, hard-rule violation SQL representation, `bel_` prefix
normalization, short-circuit attachment state, and Pydantic schema construction
from a synthetic fingerprint.

## References

- `docs/PAPER_QUALITY_SYSTEM_DESIGN_2026-04-23.md` §2.
- `docs/PAPER_QUALITY_BLACKBOARD_DESIGN_2026-04-25.md`.
- Knowledge Atlas `contracts/schemas/paper_quality.sql`.
