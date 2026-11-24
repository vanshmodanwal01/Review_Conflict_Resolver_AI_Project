"""Conflict and Evidence Schemas"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EvidenceItemResponse(BaseModel):
    id: str
    review_id: str
    stance: str
    excerpt: str
    relevance_weight: float
    variant_context: Optional[str] = None
    usage_context: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AIExplanationResponse(BaseModel):
    id: str
    provider: str
    model_name: str
    summary: str
    contributing_factors: List[str]
    supporting_evidence_summary: Optional[str] = None
    opposing_evidence_summary: Optional[str] = None
    missing_information: Optional[str] = None
    confidence_score: float
    contextual_hypotheses: Dict[str, Any] = {}
    model_config = ConfigDict(from_attributes=True)


class ConflictGroupSummary(BaseModel):
    conflict_id: str
    aspect_category: str
    conflict_score: float
    positive_review_count: int
    negative_review_count: int
    neutral_review_count: int
    headline: Optional[str] = None
    status: str
    has_explanation: bool
    confidence_score: Optional[float] = None


class ConflictGroupDetailResponse(BaseModel):
    conflict_id: str
    product_id: str
    product_title: str
    aspect_category: str
    conflict_score: float
    positive_review_count: int
    negative_review_count: int
    neutral_review_count: int
    headline: Optional[str] = None
    status: str
    detected_at: datetime
    evidence_items: List[EvidenceItemResponse] = []
    explanation: Optional[AIExplanationResponse] = None
    model_config = ConfigDict(from_attributes=True)
