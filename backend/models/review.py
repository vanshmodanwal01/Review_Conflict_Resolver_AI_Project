"""Review, ReviewSource, Aspect, Context, and Embedding Models"""
from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.base import TimestampMixin, generate_uuid, get_utc_now


class ReviewSource(Base, TimestampMixin):
    __tablename__ = "review_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), unique=True, nullable=False)
    base_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    rate_limit_per_min = Column(Integer, default=30)

    reviews = relationship("Review", back_populates="source")


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("review_sources.id"), nullable=True, index=True)
    variant_id = Column(String(36), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True)
    
    external_id = Column(String(255), nullable=True, index=True)
    rating = Column(Float, nullable=False)
    title = Column(String(255), nullable=True)
    review_text = Column(Text, nullable=False)
    reviewer_name = Column(String(100), nullable=True)
    review_date = Column(DateTime, default=get_utc_now, nullable=False)
    verified_purchase = Column(Boolean, default=True)
    language = Column(String(10), default="en")
    helpful_count = Column(Integer, default=0)
    extra_metadata = Column(JSON, default=dict)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    source = relationship("ReviewSource", back_populates="reviews")
    variant = relationship("ProductVariant", back_populates="reviews")
    aspects = relationship("ReviewAspect", back_populates="review", cascade="all, delete-orphan")
    context = relationship("ReviewContext", back_populates="review", uselist=False, cascade="all, delete-orphan")
    embedding = relationship("ReviewEmbedding", back_populates="review", uselist=False, cascade="all, delete-orphan")


class ReviewAspect(Base):
    __tablename__ = "review_aspects"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_category = Column(String(50), nullable=False, index=True)  # e.g. battery, performance, thermals
    sentiment = Column(String(20), nullable=False, index=True)  # positive, negative, neutral
    sentiment_score = Column(Float, nullable=False)  # -1.0 to 1.0
    evidence_snippet = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)

    review = relationship("Review", back_populates="aspects")


class ReviewContext(Base):
    __tablename__ = "review_contexts"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    usage_intensity = Column(String(20), default="unknown")  # low, medium, high, unknown
    primary_use_case = Column(String(50), default="general")  # gaming, programming, office, editing, casual
    environment = Column(String(50), default="unknown")  # desk, lap, travel, hot_climate, ac_room
    expectation_benchmark = Column(String(100), nullable=True)  # e.g. "comparing with MacBook", "upgraded from old HDD"
    user_experience_level = Column(String(50), default="unknown")
    extracted_attributes = Column(JSON, default=dict)
    certainty = Column(String(20), default="inferred")  # explicit, inferred, unknown

    review = relationship("Review", back_populates="context")


class ReviewEmbedding(Base):
    __tablename__ = "review_embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    review_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    # Stored as JSON list of floats for ubiquitous compatibility across SQLite & PostgreSQL
    embedding_data = Column(JSON, nullable=False)
    model_name = Column(String(100), default="sentence-transformers/all-MiniLM-L6-v2")
    created_at = Column(DateTime, default=get_utc_now)

    review = relationship("Review", back_populates="embedding")
