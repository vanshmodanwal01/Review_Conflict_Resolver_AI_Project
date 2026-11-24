"""Conflict Group Retrieval and Forensic Inspection Service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.product import Product
from backend.models.conflict import ConflictGroup, ConflictEvidence, AIExplanation
from backend.schemas.conflict import (
    ConflictGroupSummary,
    ConflictGroupDetailResponse,
    EvidenceItemResponse,
    AIExplanationResponse
)
from backend.schemas.insight import PersonalizedInsightRequest, PersonalizedInsightResponse
from backend.ai.services.personalized_insight_service import personalized_insight_service
from backend.core.logging import logger


class ConflictService:
    @staticmethod
    def get_conflicts_for_product(db: Session, product_id: str) -> List[ConflictGroupSummary]:
        conflicts = db.query(ConflictGroup).filter(ConflictGroup.product_id == product_id).all()
        summaries = []
        for c in conflicts:
            conf_score = c.explanation.confidence_score if c.explanation else None
            summaries.append(ConflictGroupSummary(
                conflict_id=c.id,
                aspect_category=c.aspect_category,
                conflict_score=c.conflict_score,
                positive_review_count=c.positive_review_count,
                negative_review_count=c.negative_review_count,
                neutral_review_count=c.neutral_review_count,
                headline=c.headline,
                status=c.status,
                has_explanation=bool(c.explanation),
                confidence_score=conf_score
            ))
        return summaries

    @staticmethod
    def get_conflict_details(db: Session, conflict_id: str) -> Optional[ConflictGroupDetailResponse]:
        c = db.query(ConflictGroup).filter(ConflictGroup.id == conflict_id).first()
        if not c:
            return None

        product = db.query(Product).filter(Product.id == c.product_id).first()

        evidence_items = []
        for ev in c.evidence_items:
            evidence_items.append(EvidenceItemResponse(
                id=ev.id,
                review_id=ev.review_id,
                stance=ev.stance,
                excerpt=ev.excerpt,
                relevance_weight=ev.relevance_weight,
                variant_context=ev.variant_context,
                usage_context=ev.usage_context
            ))

        explanation_resp = None
        if c.explanation:
            exp = c.explanation
            explanation_resp = AIExplanationResponse(
                id=exp.id,
                provider=exp.provider,
                model_name=exp.model_name,
                summary=exp.summary,
                contributing_factors=exp.contributing_factors or [],
                supporting_evidence_summary=exp.supporting_evidence_summary,
                opposing_evidence_summary=exp.opposing_evidence_summary,
                missing_information=exp.missing_information,
                confidence_score=exp.confidence_score,
                contextual_hypotheses=exp.contextual_hypotheses or {}
            )

        return ConflictGroupDetailResponse(
            conflict_id=c.id,
            product_id=c.product_id,
            product_title=product.title if product else "Unknown Product",
            aspect_category=c.aspect_category,
            conflict_score=c.conflict_score,
            positive_review_count=c.positive_review_count,
            negative_review_count=c.negative_review_count,
            neutral_review_count=c.neutral_review_count,
            headline=c.headline,
            status=c.status,
            detected_at=c.detected_at,
            evidence_items=evidence_items,
            explanation=explanation_resp
        )

    @staticmethod
    def get_personalized_advisory(
        db: Session,
        request: PersonalizedInsightRequest
    ) -> Optional[PersonalizedInsightResponse]:
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            return None

        conflicts = db.query(ConflictGroup).filter(ConflictGroup.product_id == request.product_id).all()
        return personalized_insight_service.generate_personalized_insights(product, conflicts, request)

conflict_service = ConflictService()
