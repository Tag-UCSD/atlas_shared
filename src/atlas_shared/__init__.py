from .cli_adjudicator import (
    AGCommandAdjudicator,
    ClaudeCLIAdjudicator,
    CodexCLIAdjudicator,
    ShellCommandAdjudicator,
    build_relevance_adjudication_prompt,
)
from .registry_sink import (
    RegistryFact,
    SupportsClassificationRegistry,
)
from .bundle_router import (
    BundleRoutingResult,
    QuestionBundleRouter,
    TopicBundleCandidate,
)
from .classifier_system import (
    AdaptiveClassificationResult,
    AdaptiveClassifierSubsystem,
    ClassificationEvidence,
    ClassificationStageRecord,
    HeuristicTopicOverlayMatcher,
    LocalPDFSurfaceExtractor,
    PDFSurfaceSnapshot,
    QuestionSummary,
    TopicOverlayMatch,
    TopicOverlayRecord,
)
from .article_types import (
    ArticleTypeDecision,
    HeuristicArticleTypeClassifier,
)
from .intake import (
    DomainRelevance,
    IntakeDecision,
    PreExtractionArticleIntake,
    PreExtractionIntakeGate,
    PreExtractionIntakeResult,
    RoutingTarget,
)
from .topic_bank import (
    TopicConstitutionBank,
    TopicConstitutionRecord,
    load_question_constitutions,
    load_topic_constitution_bank,
    topic_records_for_questions,
)
from .relevance import (
    AdjudicationRequest,
    AdjudicationResult,
    ArticleBundle,
    ArticleCandidate,
    QuestionArticleRelevanceFilter,
    QuestionConstitution,
    RelevanceAssessment,
)
from .paper_quality import (
    EffectSize,
    FingerprintField,
    HardRuleViolation,
    PaperQualityFingerprint,
    QualityFingerprintEnvelope,
    PowerRecord,
    PreregRecord,
    SampleOverlapEdge,
    SourceExcerpt,
)

__version__ = "0.3.0"

__all__ = [
    "AdaptiveClassificationResult",
    "AdaptiveClassifierSubsystem",
    "ArticleCandidate",
    "BundleRoutingResult",
    "PaperQualityFingerprint",
    "PreExtractionIntakeGate",
    "QuestionArticleRelevanceFilter",
    "QuestionBundleRouter",
    "QuestionConstitution",
    "RelevanceAssessment",
    "RegistryFact",
    "load_topic_constitution_bank",
]
