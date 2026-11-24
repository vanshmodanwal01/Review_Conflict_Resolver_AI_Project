"""Review Ingestion and Retrieval Services"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.review import Review, ReviewSource, ReviewAspect, ReviewContext
from backend.schemas.review import ReviewCreate
from backend.core.logging import logger


class ReviewService:
    @staticmethod
    def get_or_create_source(db: Session, source_name: str, base_url: Optional[str] = None) -> ReviewSource:
        source = db.query(ReviewSource).filter(ReviewSource.name == source_name).first()
        if not source:
            source = ReviewSource(name=source_name, base_url=base_url)
            db.add(source)
            db.commit()
            db.refresh(source)
        return source

    @staticmethod
    def get_reviews_for_product(
        db: Session,
        product_id: str,
        limit: int = 100,
        offset: int = 0,
        aspect_filter: Optional[str] = None
    ) -> List[Review]:
        q = db.query(Review).filter(Review.product_id == product_id)
        if aspect_filter:
            q = q.join(ReviewAspect).filter(ReviewAspect.aspect_category == aspect_filter)
        return q.order_by(desc(Review.review_date)).offset(offset).limit(limit).all()

    @staticmethod
    def add_review(db: Session, review_in: ReviewCreate) -> Review:
        source = ReviewService.get_or_create_source(db, review_in.source_name or "Curated Dataset")
        review = Review(
            product_id=review_in.product_id,
            source_id=source.id,
            external_id=review_in.external_id,
            rating=review_in.rating,
            title=review_in.title,
            review_text=review_in.review_text,
            reviewer_name=review_in.reviewer_name,
            review_date=review_in.review_date,
            verified_purchase=review_in.verified_purchase,
            language=review_in.language
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
