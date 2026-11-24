"""Product Discovery & Catalog Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.api.deps import DbSession
from backend.services.product_service import ProductService
from backend.schemas.product import ProductResponse, ProductSearchQuery, ProductCreate
from backend.collectors.provider_manager import provider_manager


router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def list_products(category: str = "laptops", limit: int = 50, db: Session = DbSession):
    """Lists products stored in database."""
    return ProductService.list_products(db, category=category, limit=limit)

@router.post("/search", response_model=List[ProductResponse])
def search_products(query: ProductSearchQuery, db: Session = DbSession):
    """
    Searches product catalog.
    If database results are empty or few, federates search across allowed providers.
    """
    db_results = ProductService.search_products(db, query)
    if db_results:
        return db_results

    # Cross-source discovery via ProviderManager
    external_matches = provider_manager.search_all_sources(query.query, limit=query.limit)
    created_products = []
    for item in external_matches:
        p_create = ProductCreate(
            title=item["title"],
            brand=item["brand"],
            category=item.get("category", "laptops"),
            model_number=item.get("external_id"),
            specifications=item.get("specifications", {})
        )
        p = ProductService.create_product(db, p_create)
        created_products.append(p)

    return created_products if created_products else db_results

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = DbSession):
    """Retrieves single product metadata by UUID."""
    product = ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found."
        )
    return product
