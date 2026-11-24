"""Personalized Insight Advisory Service"""
from typing import Dict, Any, List
from backend.models.product import Product
from backend.models.conflict import ConflictGroup
from backend.schemas.insight import PersonalizedInsightRequest, PersonalizedInsightResponse, AspectAdvisory
from backend.core.logging import logger


class PersonalizedInsightService:
    """
    Translates detected review conflicts into tailored buying advisories
    based on the customer's intended use-case, intensity, and configuration.
    """

    @staticmethod
    def generate_personalized_insights(
        product: Product,
        conflicts: List[ConflictGroup],
        request: PersonalizedInsightRequest
    ) -> PersonalizedInsightResponse:
        
        advisories: List[AspectAdvisory] = []
        high_risk_count = 0

        # Map aspects to user priorities
        for aspect_name in request.priority_aspects:
            # Find if this aspect has a detected conflict
            conflict = next((c for c in conflicts if c.aspect_category == aspect_name), None)

            if conflict and conflict.explanation:
                exp = conflict.explanation
                factors = exp.contributing_factors or []
                
                # Check if user's workload or target variant matches negative factors
                is_intensity_match = (
                    request.usage_intensity == "high" and 
                    any("high" in f.lower() or "heavy" in f.lower() or "render" in f.lower() or "gaming" in f.lower() for f in factors)
                )
                is_variant_match = (
                    request.target_variant and 
                    any(word.lower() in str(factors).lower() for word in request.target_variant.split())
                )

                if is_intensity_match or is_variant_match:
                    risk = "high"
                    high_risk_count += 1
                    predicted = "Significantly degraded experience expected under your workload."
                    explanation_text = (
                        f"Your planned {request.usage_intensity}-intensity workflow and variant choices align directly "
                        f"with dissatisfied reviewer cohorts. {exp.summary}"
                    )
                else:
                    risk = "moderate"
                    predicted = "Variable experience depending on environment and workload."
                    explanation_text = exp.summary

                quote = exp.opposing_evidence_summary if risk == "high" else exp.supporting_evidence_summary

                advisories.append(AspectAdvisory(
                    aspect=aspect_name,
                    predicted_experience=predicted,
                    risk_level=risk,
                    explanation=explanation_text,
                    conflicting_factors_to_note=factors,
                    relevant_evidence_quote=quote
                ))
            else:
                advisories.append(AspectAdvisory(
                    aspect=aspect_name,
                    predicted_experience="Consistent experience reported by customers.",
                    risk_level="low",
                    explanation=f"No major polarity conflict detected regarding {aspect_name.replace('_', ' ')}.",
                    conflicting_factors_to_note=[],
                    relevant_evidence_quote=None
                ))

        # Overall Recommendation Tier
        if high_risk_count >= 2:
            tier = "proceed_with_caution"
            overview = (
                f"Proceed with caution: Customer evidence reveals significant conflicts in key areas ({', '.join(request.priority_aspects)}) "
                f"that negatively impact {request.intended_use_case} at {request.usage_intensity} intensity."
            )
        elif high_risk_count == 1:
            tier = "conditionally_recommended"
            overview = (
                f"Conditionally recommended: Suitable for {request.intended_use_case}, but be prepared for known tradeoffs "
                f"identified in customer reviews."
            )
        else:
            tier = "highly_recommended"
            overview = (
                f"Highly recommended: Customer review patterns indicate strong satisfaction for {request.intended_use_case} "
                f"with minimal conflicting feedback."
            )

        return PersonalizedInsightResponse(
            product_id=product.id,
            product_title=product.title,
            user_profile_summary=f"{request.intended_use_case.replace('_', ' ').title()} ({request.usage_intensity} intensity) on {request.target_variant or 'standard configuration'}",
            overall_recommendation_tier=tier,
            advisory_summary=overview,
            aspect_advisories=advisories,
            confidence_score=0.89,
            disclaimer="Advisory generated from authentic customer review conflicts. Individual real-world experiences may vary."
        )

personalized_insight_service = PersonalizedInsightService()
