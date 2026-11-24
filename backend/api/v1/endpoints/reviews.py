"""Review Inspection and Ingestion Endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.api.deps import DbSession
from backend.services.review_service import ReviewService
from backend.services.product_service import ProductService
from backend.schemas.review import ReviewResponse, ReviewCreate
from backend.collectors.provider_manager import provider_manager


router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/{product_id}", response_model=List[ReviewResponse])
def get_reviews_for_product(
    product_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    aspect: Optional[str] = Query(None, description="Filter reviews mentioning specific aspect"),
    db: Session = DbSession
):
    """Retrieves normalized customer reviews for a given product."""
    product = ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    reviews = ReviewService.get_reviews_for_product(db, product_id, limit=limit, offset=offset, aspect_filter=aspect)
    
    # If no reviews in database, fetch from provider manager and persist
    if not reviews and offset == 0:
        norm_reviews = provider_manager.collect_reviews_for_product(product.model_number or product.id)
        for nr in norm_reviews:
            r_in = ReviewCreate(
                product_id=product.id,
                source_name=nr.source,
                external_id=nr.external_product_id,
                rating=nr.rating,
                title=f"Review for {nr.product_name}",
                review_text=nr.review_text,
                reviewer_name=nr.reviewer_name,
                verified_purchase=nr.verified_purchase,
                raw_variant=nr.variant
            )
            ReviewService.add_review(db, r_in)
        
        # Refresh product review count
        reviews = ReviewService.get_reviews_for_product(db, product_id, limit=limit, offset=offset, aspect_filter=aspect)
        product.total_reviews = len(reviews)
        db.commit()

    # Format response
    results = []
    for r in reviews:
        results.append(ReviewResponse(
            id=r.id,
            product_id=r.product_id,
            source_name=r.source.name if r.source else "Curated Dataset",
            variant_details=r.variant.raw_variant_string if r.variant else None,
            rating=r.rating,
            title=r.title,
            review_text=r.review_text,
            reviewer_name=r.reviewer_name,
            review_date=r.review_date,
            verified_purchase=r.verified_purchase,
            language=r.language,
            created_at=r.created_at,
            aspects=[
                {
                    "id": a.id,
                    "aspect_category": a.aspect_category,
                    "sentiment": a.sentiment,
                    "sentiment_score": a.sentiment_score,
                    "evidence_snippet": a.evidence_snippet
                }
                for a in r.aspects
            ],
            context={
                "id": r.context.id,
                "usage_intensity": r.context.usage_intensity,
                "primary_use_case": r.context.primary_use_case,
                "environment": r.context.environment,
                "expectation_benchmark": r.context.expectation_benchmark,
                "certainty": r.context.certainty,
                "extracted_attributes": r.context.extracted_attributes or {}
            } if r.context else None
        ))
    return results
