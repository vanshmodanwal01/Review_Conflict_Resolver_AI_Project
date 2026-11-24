"""Personalized User Insights Schemas"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PersonalizedInsightRequest(BaseModel):
    product_id: str
    target_variant: Optional[str] = Field(None, description="e.g., 16GB RAM, 4K OLED, Intel Core i7")
    intended_use_case: str = Field(..., description="e.g. software_development, gaming, content_creation, office_work, college_study")
    usage_intensity: str = Field(default="medium", description="low, medium, high")
    environment: Optional[str] = Field("desk", description="desk, lap, travel, warm_room")
    priority_aspects: List[str] = Field(default=["battery", "performance", "thermals_and_noise"])


class AspectAdvisory(BaseModel):
    aspect: str
    predicted_experience: str
    risk_level: str  # low, moderate, high
    explanation: str
    conflicting_factors_to_note: List[str]
    relevant_evidence_quote: Optional[str] = None


class PersonalizedInsightResponse(BaseModel):
    product_id: str
    product_title: str
    user_profile_summary: str
    overall_recommendation_tier: str  # highly_recommended, conditionally_recommended, proceed_with_caution, not_recommended
    advisory_summary: str
    aspect_advisories: List[AspectAdvisory]
    confidence_score: float
    disclaimer: str
