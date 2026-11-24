"""Analysis Orchestration Service"""
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.product import Product
from backend.models.review import Review, ReviewAspect, ReviewContext, ReviewEmbedding
from backend.models.analysis import AnalysisJob
from backend.models.conflict import ConflictGroup, ConflictEvidence, AIExplanation
from backend.ai.preprocessing import preprocessor
from backend.ai.aspect_extractor import aspect_extractor
from backend.ai.context_extractor import context_extractor
from backend.ai.embedding_service import embedding_service
from backend.ai.conflict_engine import conflict_engine
from backend.ai.services.explanation_service import explanation_service
from backend.schemas.analysis import ProductAnalysisSummaryResponse, AspectSentimentSummary
from backend.core.logging import logger


class AnalysisService:
    """
    Coordinates review analysis, NLP aspect extraction, context mining,
    dense vector embedding generation, conflict discovery, and explanation synthesis.
    """

    @staticmethod
    async def process_product_analysis(
        db: Session,
        product_id: str,
        job_id: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        logger.info(f"Starting end-to-end analysis for product {product_id}...")
        
        # 1. Update job status if running asynchronously
        job = None
        if job_id:
            job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
            if job:
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
                db.commit()

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            if job:
                job.status = "failed"
                job.error_message = f"Product {product_id} not found."
                db.commit()
            return {"error": "Product not found"}

        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        if not reviews:
            logger.info("No reviews stored yet for product. Auto-seeding from curated provider...")
            from backend.collectors.curated_dataset import CuratedDatasetCollector
            collector = CuratedDatasetCollector()
            collector.fetch_reviews(product.model_number or product.id)
            reviews = db.query(Review).filter(Review.product_id == product_id).all()

        total_reviews = len(reviews)
        if job:
            job.total_reviews = total_reviews
            db.commit()

        # 2. Extract aspects, context, and embeddings for all reviews
        analyzed_review_payloads = []

        for idx, r in enumerate(reviews, 1):
            # Check if aspects already exist
            existing_aspects = db.query(ReviewAspect).filter(ReviewAspect.review_id == r.id).all()
            if force_refresh or not existing_aspects:
                # Clear existing
                db.query(ReviewAspect).filter(ReviewAspect.review_id == r.id).delete()
                db.query(ReviewContext).filter(ReviewContext.review_id == r.id).delete()
                db.query(ReviewEmbedding).filter(ReviewEmbedding.review_id == r.id).delete()

                # Aspect extraction
                extracted = aspect_extractor.extract_aspects(r.review_text)
                db_aspects = []
                for asp in extracted:
                    a = ReviewAspect(
                        review_id=r.id,
                        aspect_category=asp["aspect_category"],
                        sentiment=asp["sentiment"],
                        sentiment_score=asp["sentiment_score"],
                        evidence_snippet=asp["evidence_snippet"],
                        char_start=asp["char_start"],
                        char_end=asp["char_end"]
                    )
                    db.add(a)
                    db_aspects.append(a)

                # Context extraction
                variant_str = r.variant.raw_variant_string if r.variant else None
                ctx = context_extractor.extract_context(r.review_text, declared_variant=variant_str)
                c_model = ReviewContext(
                    review_id=r.id,
                    usage_intensity=ctx["usage_intensity"],
                    primary_use_case=ctx["primary_use_case"],
                    environment=ctx["environment"],
                    expectation_benchmark=ctx["expectation_benchmark"],
                    certainty=ctx["certainty"],
                    extracted_attributes=ctx["extracted_attributes"]
                )
                db.add(c_model)

                # Embedding generation
                vec = embedding_service.embed_text(r.review_text)
                emb = ReviewEmbedding(
                    review_id=r.id,
                    embedding_data=vec,
                    model_name=embedding_service.model_name
                )
                db.add(emb)
                db.commit()
            else:
                db_aspects = existing_aspects
                c_model = db.query(ReviewContext).filter(ReviewContext.review_id == r.id).first()

            # Compile payload for conflict engine
            analyzed_review_payloads.append({
                "id": r.id,
                "rating": r.rating,
                "review_text": r.review_text,
                "variant": r.variant.raw_variant_string if r.variant else (c_model.extracted_attributes.get("declared_variant") if c_model else None),
                "context": {
                    "usage_intensity": c_model.usage_intensity if c_model else "unknown",
                    "primary_use_case": c_model.primary_use_case if c_model else "general",
                    "environment": c_model.environment if c_model else "unknown"
                },
                "aspects": [
                    {
                        "id": a.id,
                        "aspect_category": a.aspect_category,
                        "sentiment": a.sentiment,
                        "sentiment_score": a.sentiment_score,
                        "evidence_snippet": a.evidence_snippet
                    }
                    for a in db_aspects
                ]
            })

            if job and idx % 2 == 0:
                job.processed_reviews = idx
                job.progress_percent = int((idx / max(1, total_reviews)) * 50)
                db.commit()

        # 3. Detect Conflicts
        detected_conflicts = conflict_engine.detect_conflicts(product_id, analyzed_review_payloads)
        
        # Clear existing conflicts if re-running
        db.query(ConflictGroup).filter(ConflictGroup.product_id == product_id).delete()
        db.commit()

        # 4. Save Conflicts and Synthesize Grounded Explanations
        saved_conflicts = []
        for c in detected_conflicts:
            cg = ConflictGroup(
                product_id=product_id,
                aspect_category=c["aspect_category"],
                conflict_score=c["conflict_score"],
                positive_review_count=c["positive_review_count"],
                negative_review_count=c["negative_review_count"],
                neutral_review_count=c["neutral_review_count"],
                headline=c["headline"],
                status="resolved_with_explanation"
            )
            db.add(cg)
            db.flush()

            # Add Evidence Items
            for ev in c["evidence_items"]:
                ce = ConflictEvidence(
                    conflict_group_id=cg.id,
                    review_id=ev["review_id"],
                    aspect_id=ev.get("aspect_id"),
                    stance=ev["stance"],
                    relevance_weight=ev["relevance_weight"],
                    excerpt=ev["excerpt"],
                    variant_context=ev.get("variant_context"),
                    usage_context=ev.get("usage_context")
                )
                db.add(ce)

            # Generate Grounded Explanation
            pos_evidence = [e for e in c["evidence_items"] if e["stance"] == "positive"]
            neg_evidence = [e for e in c["evidence_items"] if e["stance"] == "negative"]
            divergence_notes = c["divergence_analysis"].get("hypotheses", [])

            exp_data = await explanation_service.generate_explanation(
                product_title=product.title,
                aspect_category=c["aspect_category"],
                positive_evidence=pos_evidence,
                negative_evidence=neg_evidence,
                divergence_notes=divergence_notes
            )

            exp = AIExplanation(
                conflict_group_id=cg.id,
                provider=exp_data.get("provider", "gemini"),
                model_name=exp_data.get("model_name", "gemini-1.5-flash"),
                summary=exp_data["summary"],
                contributing_factors=exp_data.get("contributing_factors", []),
                supporting_evidence_summary=exp_data.get("supporting_evidence_summary"),
                opposing_evidence_summary=exp_data.get("opposing_evidence_summary"),
                missing_information=exp_data.get("missing_information"),
                confidence_score=exp_data.get("confidence_score", 0.5),
                tokens_consumed=exp_data.get("tokens_consumed", 0),
                contextual_hypotheses=exp_data.get("contextual_hypotheses", {})
            )
            db.add(exp)
            saved_conflicts.append(cg)

        db.commit()

        if job:
            job.status = "completed"
            job.progress_percent = 100
            job.processed_reviews = total_reviews
            job.detected_conflicts = len(saved_conflicts)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

        logger.info(f"Analysis completed for product {product_id}. {len(saved_conflicts)} conflicts resolved.")
        return {
            "product_id": product_id,
            "total_reviews": total_reviews,
            "detected_conflicts_count": len(saved_conflicts)
        }

    @staticmethod
    def get_analysis_summary(db: Session, product_id: str) -> Optional[ProductAnalysisSummaryResponse]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        total_revs = len(reviews)
        avg_rating = round(sum(r.rating for r in reviews) / max(1, total_revs), 2)

        # Rating distribution
        rating_dist = {"1_star": 0, "2_star": 0, "3_star": 0, "4_star": 0, "5_star": 0}
        for r in reviews:
            star_key = f"{int(round(r.rating))}_star"
            if star_key in rating_dist:
                rating_dist[star_key] += 1

        # Sentiment breakdown from aspects
        aspects = (
            db.query(ReviewAspect)
            .join(Review, ReviewAspect.review_id == Review.id)
            .filter(Review.product_id == product_id)
            .all()
        )

        sent_dist = {"positive": 0, "negative": 0, "neutral": 0}
        aspect_map = defaultdict(lambda: {"pos": 0, "neg": 0, "neu": 0, "scores": []})

        for a in aspects:
            sent_dist[a.sentiment] = sent_dist.get(a.sentiment, 0) + 1
            if a.sentiment == "positive":
                aspect_map[a.aspect_category]["pos"] += 1
            elif a.sentiment == "negative":
                aspect_map[a.aspect_category]["neg"] += 1
            else:
                aspect_map[a.aspect_category]["neu"] += 1
            aspect_map[a.aspect_category]["scores"].append(a.sentiment_score)

        # Check existing conflicts
        conflict_aspects = {
            c.aspect_category
            for c in db.query(ConflictGroup).filter(ConflictGroup.product_id == product_id).all()
        }

        aspect_breakdowns = []
        for cat, data in aspect_map.items():
            tot = data["pos"] + data["neg"] + data["neu"]
            net_score = round(sum(data["scores"]) / max(1, len(data["scores"])), 2)
            aspect_breakdowns.append(AspectSentimentSummary(
                aspect=cat,
                positive_count=data["pos"],
                negative_count=data["neg"],
                neutral_count=data["neu"],
                total_mentions=tot,
                net_sentiment_score=net_score,
                has_conflict=cat in conflict_aspects
            ))

        return ProductAnalysisSummaryResponse(
            product_id=product.id,
            product_title=product.title,
            total_reviews=total_revs,
            average_rating=avg_rating,
            rating_distribution=rating_dist,
            sentiment_distribution=sent_dist,
            aspect_breakdown=aspect_breakdowns,
            detected_conflicts_count=len(conflict_aspects),
            last_analyzed_at=datetime.now(timezone.utc)
        )

analysis_service = AnalysisService()
