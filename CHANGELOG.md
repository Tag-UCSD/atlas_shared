# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on Keep a Changelog.

## [Unreleased]

### Added

- Canonical home for the cross-repo science-writing norm documents, now hosted
  in `contracts/`: `SCIENCE_COMMUNICATION_NORMS.md`, `WRITING_STYLE_GUIDE.md`,
  `VISUALIZATION_NORMS.md`, and `EPISTEMIC_PRINCIPLES.md`. These were previously
  duplicated across `Article_Eater_PostQuinean_v1`, `_v1_recovery`,
  `_v1_recovery_kg`, and `AE_clean_push`. `atlas_shared` is now the single
  source of truth; `Article_Eater_PostQuinean_v1_recovery` references them via
  relative symlinks (`contracts/` and `docs/EPISTEMIC_PRINCIPLES.md`). The
  `science-writer-summary` skill's contract chain resolves through the symlinks
  unchanged.

## [0.3.0] - 2026-04-22

### Added

- `RegistryFact.paper_id` as a top-level field.
- `SchemaVersion` Literal typing for registry-fact schema versions.
- `src/atlas_shared/_util.py` for shared private helpers.
- `src/atlas_shared/data/domain_lexicon.json`.
- `src/atlas_shared/data/article_type_defaults.json`.
- `atlas_shared.__version__`.
- package version test coverage.
- explicit public-API policy in `AGENTS.md`.
- explicit canonical `paper_id` naming in `contracts/ATLAS_SHARED_SCOPE_CONTRACT_2026-04-07.md`.

### Changed

- `QuestionConstitution.bundle_id` now includes `question_id` to avoid collisions when constitutions share a topic.
- keyword false-positive intake handling now distinguishes clear hard rejects from soft manual-review terms.
- intake domain lexicon is now data-backed and overrideable.
- article-type defaults are now data-backed rather than hardcoded in the dataclass declaration.
- `atlas_shared.__all__` now exposes only the ten canonical entry points.

### Deprecated

- `RegistryFact.details_json["paper_id"]` remains for compatibility, but duplicates the canonical top-level `paper_id` field and should be treated as transitional.

## [0.2.0] - 2026-04-21

### Added

- adaptive classifier subsystem
- topic constitution bank

## [0.1.0] - 2026-04-07

### Added

- initial `atlas_shared` publish
