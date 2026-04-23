# Repo Agent Contract

This repo is the shared classification and relevance contract layer for Atlas.

## Do Not Reinvent

Before creating any article-type classifier, relevance gate, topic router, or
first-pass PDF intake logic in another Atlas repo, inspect this repo first.

Canonical shared modules:

- `atlas_shared.intake.PreExtractionIntakeGate`
- `atlas_shared.topic_bank.load_topic_constitution_bank`
- `atlas_shared.relevance.QuestionArticleRelevanceFilter`
- `atlas_shared.bundle_router.QuestionBundleRouter`
- `atlas_shared.article_types.HeuristicArticleTypeClassifier`

Canonical contracts:

- `contracts/PRE_EXTRACTION_INTAKE_CONTRACT_2026-04-17.md`
- `contracts/PANEL_TOPIC_EVIDENCE_CONTRACT_2026-04-17.md`

## Public API Rule

The ten symbols in `atlas_shared.__all__` are the public API:

- `AdaptiveClassifierSubsystem`
- `ArticleCandidate`
- `BundleRoutingResult`
- `PreExtractionIntakeGate`
- `QuestionArticleRelevanceFilter`
- `QuestionBundleRouter`
- `QuestionConstitution`
- `RegistryFact`
- `RelevanceAssessment`
- `load_topic_constitution_bank`

Anything else is internal. Consumers may import it from submodules if they
must, but they should do so knowing those imports may break during refactor.

## Panel Evidence Rule

The student-facing questions are topic constitutions. The panel dossiers in
`docs/panels/` and the curated bank in
`src/atlas_shared/data/question_constitutions_curated_30.json` are part of the
evidence base for classification, intake, edge-case detection, topic expansion,
and routing.

Do not treat those files as only Google Scholar prompt material.

## First Gate Rule

The first PDF gate is pre-extraction. It may use arrival metadata, title,
abstract, tags, keywords, and first-page text. It must not use Article Eater V7
dependent-variable or measurement extraction outputs.

Only clear false positives may be rejected. Plausible adjacent or novel papers
must be preserved as `edge_case`, `manual_review`, `topic_expansion_candidate`,
or `new_topic_candidate`.
