"""Schema Package Exports"""
from backend.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductSearchQuery,
    VariantCreate,
    VariantResponse
)
from backend.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewNormalizationResult,
    AspectResponse,
    ContextResponse
)
from backend.schemas.analysis import (
    AnalysisTriggerRequest,
    AnalysisJobResponse,
    ProductAnalysisSummaryResponse,
    AspectSentimentSummary
)
from backend.schemas.conflict import (
    ConflictGroupSummary,
    ConflictGroupDetailResponse,
    EvidenceItemResponse,
    AIExplanationResponse
)
from backend.schemas.insight import (
    PersonalizedInsightRequest,
    PersonalizedInsightResponse,
    AspectAdvisory
)

__all__ = [
    "ProductCreate",
    "ProductResponse",
    "ProductSearchQuery",
    "VariantCreate",
    "VariantResponse",
    "ReviewCreate",
    "ReviewResponse",
    "ReviewNormalizationResult",
    "AspectResponse",
    "ContextResponse",
    "AnalysisTriggerRequest",
    "AnalysisJobResponse",
    "ProductAnalysisSummaryResponse",
    "AspectSentimentSummary",
    "ConflictGroupSummary",
    "ConflictGroupDetailResponse",
    "EvidenceItemResponse",
    "AIExplanationResponse",
    "PersonalizedInsightRequest",
    "PersonalizedInsightResponse",
    "AspectAdvisory"
]
