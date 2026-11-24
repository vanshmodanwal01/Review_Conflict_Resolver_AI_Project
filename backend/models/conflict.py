"""Conflict Group, Evidence, and AI Explanation Models"""
from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.base import TimestampMixin, generate_uuid, get_utc_now


class ConflictGroup(Base, TimestampMixin):
    __tablename__ = "conflict_groups"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_category = Column(String(50), nullable=False, index=True)  # e.g., battery, performance, thermals
    conflict_score = Column(Float, nullable=False)  # 0.0 to 1.0 (disagreement magnitude)
    positive_review_count = Column(Integer, default=0)
    negative_review_count = Column(Integer, default=0)
    neutral_review_count = Column(Integer, default=0)
    headline = Column(String(255), nullable=True)
    status = Column(String(50), default="detected", index=True)  # detected, resolved, unexplained
    detected_at = Column(DateTime, default=get_utc_now)

    # Relationships
    product = relationship("Product", back_populates="conflict_groups")
    evidence_items = relationship("ConflictEvidence", back_populates="conflict_group", cascade="all, delete-orphan")
    explanation = relationship("AIExplanation", back_populates="conflict_group", uselist=False, cascade="all, delete-orphan")


class ConflictEvidence(Base):
    __tablename__ = "conflict_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    conflict_group_id = Column(String(36), ForeignKey("conflict_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(String(36), ForeignKey("review_aspects.id", ondelete="SET NULL"), nullable=True)
    
    stance = Column(String(20), nullable=False)  # positive, negative, contradictory
    relevance_weight = Column(Float, default=1.0)
    excerpt = Column(Text, nullable=False)
    variant_context = Column(String(255), nullable=True)
    usage_context = Column(String(255), nullable=True)

    conflict_group = relationship("ConflictGroup", back_populates="evidence_items")
    review = relationship("Review")
    aspect = relationship("ReviewAspect")


class AIExplanation(Base, TimestampMixin):
    __tablename__ = "ai_explanations"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    conflict_group_id = Column(String(36), ForeignKey("conflict_groups.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    provider = Column(String(50), default="gemini")  # gemini, openai
    model_name = Column(String(100), default="gemini-1.5-flash")
    
    summary = Column(Text, nullable=False)
    contributing_factors = Column(JSON, default=list)  # List of string hypothesis factors
    supporting_evidence_summary = Column(Text, nullable=True)
    opposing_evidence_summary = Column(Text, nullable=True)
    missing_information = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0
    contextual_hypotheses = Column(JSON, default=dict)
    tokens_consumed = Column(Integer, default=0)

    conflict_group = relationship("ConflictGroup", back_populates="explanation")
