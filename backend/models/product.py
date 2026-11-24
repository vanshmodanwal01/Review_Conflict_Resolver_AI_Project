"""Product and Variant Models"""
from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base
from backend.models.base import TimestampMixin, generate_uuid


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="laptops", nullable=False, index=True)
    model_number = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    specifications = Column(JSON, default=dict, nullable=False)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    # Relationships
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    conflict_groups = relationship("ConflictGroup", back_populates="product", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base, TimestampMixin):
    __tablename__ = "product_variants"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_sku = Column(String(100), nullable=True)
    cpu = Column(String(100), nullable=True)
    ram = Column(String(50), nullable=True)
    storage = Column(String(50), nullable=True)
    gpu = Column(String(100), nullable=True)
    display_spec = Column(String(100), nullable=True)
    raw_variant_string = Column(String(255), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="variants")
    reviews = relationship("Review", back_populates="variant")
