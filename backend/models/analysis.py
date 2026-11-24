"""Analysis Job Model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.base import TimestampMixin, generate_uuid, get_utc_now


class AnalysisJob(Base, TimestampMixin):
    __tablename__ = "analysis_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, running, completed, failed
    progress_percent = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)
    processed_reviews = Column(Integer, default=0)
    detected_conflicts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    product = relationship("Product", back_populates="analysis_jobs")
