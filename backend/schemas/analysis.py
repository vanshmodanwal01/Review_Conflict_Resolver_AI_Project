"""Analysis Request and Job Schemas"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AnalysisTriggerRequest(BaseModel):
    force_refresh: bool = False
    provider_preference: Optional[str] = "all"

class AnalysisJobResponse(BaseModel):
    job_id: str
    product_id: str
    status: str
    progress_percent: int
    total_reviews: int
    processed_reviews: int
    detected_conflicts: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class AspectSentimentSummary(BaseModel):
    aspect: str
    positive_count: int
    negative_count: int
    neutral_count: int
    total_mentions: int
    net_sentiment_score: float
    has_conflict: bool


class ProductAnalysisSummaryResponse(BaseModel):
    product_id: str
    product_title: str
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]
    sentiment_distribution: Dict[str, int]
    aspect_breakdown: List[AspectSentimentSummary]
    detected_conflicts_count: int
    last_analyzed_at: Optional[datetime] = None
