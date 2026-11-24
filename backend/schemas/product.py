"""Product and Variant Pydantic Schemas"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VariantBase(BaseModel):
    variant_sku: Optional[str] = None
    cpu: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    gpu: Optional[str] = None
    display_spec: Optional[str] = None
    raw_variant_string: Optional[str] = None

class VariantCreate(VariantBase):
    pass

class VariantResponse(VariantBase):
    id: str
    product_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    brand: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="laptops", max_length=50)
    model_number: Optional[str] = None
    image_url: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)

class ProductCreate(ProductBase):
    variants: Optional[List[VariantCreate]] = None

class ProductSearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Keywords to search laptop model or brand")
    category: Optional[str] = "laptops"
    limit: Optional[int] = Field(default=10, ge=1, le=50)

class ProductResponse(ProductBase):
    id: str
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    variants: List[VariantResponse] = []
    available_sources: List[str] = []
    model_config = ConfigDict(from_attributes=True)
