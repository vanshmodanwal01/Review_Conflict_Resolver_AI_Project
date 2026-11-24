"""Review, Aspect, and Context Pydantic Schemas"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AspectResponse(BaseModel):
    id: str
    aspect_category: str
    sentiment: str
    sentiment_score: float
    evidence_snippet: str
    model_config = ConfigDict(from_attributes=True)


class ContextResponse(BaseModel):
    id: str
    usage_intensity: str
    primary_use_case: str
    environment: str
    expectation_benchmark: Optional[str] = None
    certainty: str
    extracted_attributes: Dict[str, Any] = {}
    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    external_id: Optional[str] = None
    rating: float = Field(..., ge=1.0, le=5.0)
    title: Optional[str] = None
    review_text: str = Field(..., min_length=3)
    reviewer_name: Optional[str] = None
    review_date: Optional[datetime] = None
    verified_purchase: bool = True
    language: str = "en"

class ReviewCreate(ReviewBase):
    product_id: str
    source_name: Optional[str] = "Curated Dataset"
    raw_variant: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: str
    product_id: str
    source_name: Optional[str] = None
    variant_details: Optional[str] = None
    aspects: List[AspectResponse] = []
    context: Optional[ContextResponse] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReviewNormalizationResult(BaseModel):
    source: str
    external_product_id: Optional[str] = None
    product_name: str
    rating: float
    review_text: str
    variant: Optional[str] = None
    review_date: Optional[str] = None
    reviewer_name: Optional[str] = None
    verified_purchase: bool = True
