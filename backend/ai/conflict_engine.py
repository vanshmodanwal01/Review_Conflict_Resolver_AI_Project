"""Conflict Detection and Evidence Attribution Engine"""
import math
from typing import List, Dict, Any, Optional
from collections import defaultdict
from backend.core.logging import logger


class ConflictDetectionEngine:
    """
    Identifies contradictory opinions on identical product aspects,
    analyzes contextual divergence, calculates conflict severity scores,
    and retrieves representative evidence citations.
    """

    MIN_CONFLICT_SCORE_THRESHOLD = 0.35

    def detect_conflicts(
        self,
        product_id: str,
        reviews_with_analysis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Processes normalized reviews with extracted aspects and contexts.
        Returns list of detected conflict groups with evidence items and contextual divergence.
        """
        # 1. Group by aspect category
        aspect_buckets = defaultdict(lambda: {"positive": [], "negative": [], "neutral": []})

        for r in reviews_with_analysis:
            review_id = r.get("id") or r.get("external_id")
            variant = r.get("variant")
            context = r.get("context") or {}
            
            for asp in r.get("aspects", []):
                aspect_cat = asp.get("aspect_category")
                sentiment = asp.get("sentiment")
                evidence_text = asp.get("evidence_snippet") or r.get("review_text")
                score = asp.get("sentiment_score", 0.0)

                entry = {
                    "review_id": review_id,
                    "aspect_id": asp.get("id"),
                    "rating": r.get("rating"),
                    "excerpt": evidence_text,
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "variant": variant,
                    "context": context
                }

                if sentiment == "positive":
                    aspect_buckets[aspect_cat]["positive"].append(entry)
                elif sentiment == "negative":
                    aspect_buckets[aspect_cat]["negative"].append(entry)
                else:
                    aspect_buckets[aspect_cat]["neutral"].append(entry)

        conflict_groups = []

        # 2. Evaluate each aspect for conflict
        for aspect_cat, buckets in aspect_buckets.items():
            pos_list = buckets["positive"]
            neg_list = buckets["negative"]
            neu_list = buckets["neutral"]

            pos_count = len(pos_list)
            neg_count = len(neg_list)
            total_aspect_reviews = pos_count + neg_count + len(neu_list)

            # Need at least one positive and one negative review to form a contradiction
            if pos_count == 0 or neg_count == 0:
                continue

            # Compute Conflict Score
            # Balance term: 1.0 when pos == neg
            balance = (2.0 * min(pos_count, neg_count)) / (pos_count + neg_count)
            # Volume confidence factor: scales up with sample size
            volume_factor = min(1.0, math.sqrt(pos_count + neg_count) / 1.5)
            conflict_score = round(balance * volume_factor, 3)

            if conflict_score < self.MIN_CONFLICT_SCORE_THRESHOLD:
                continue

            # 3. Analyze Contextual Divergence
            divergence_analysis = self._analyze_contextual_divergence(pos_list, neg_list)

            # 4. Assemble Evidence Citations (top representative positive and negative reviews)
            evidence_items = []
            for item in pos_list[:3]:
                evidence_items.append({
                    "review_id": item["review_id"],
                    "aspect_id": item.get("aspect_id"),
                    "stance": "positive",
                    "excerpt": item["excerpt"],
                    "relevance_weight": round(abs(item["sentiment_score"]) or 0.8, 2),
                    "variant_context": item.get("variant") or "Not Specified",
                    "usage_context": f"{item['context'].get('primary_use_case', 'general')} ({item['context'].get('usage_intensity', 'medium')} intensity)"
                })
            for item in neg_list[:3]:
                evidence_items.append({
                    "review_id": item["review_id"],
                    "aspect_id": item.get("aspect_id"),
                    "stance": "negative",
                    "excerpt": item["excerpt"],
                    "relevance_weight": round(abs(item["sentiment_score"]) or 0.8, 2),
                    "variant_context": item.get("variant") or "Not Specified",
                    "usage_context": f"{item['context'].get('primary_use_case', 'general')} ({item['context'].get('usage_intensity', 'medium')} intensity)"
                })

            headline = (
                f"Significant contradiction detected in {aspect_cat.replace('_', ' ').title()}: "
                f"{pos_count} positive vs {neg_count} negative customer experiences."
            )

            conflict_groups.append({
                "product_id": product_id,
                "aspect_category": aspect_cat,
                "conflict_score": conflict_score,
                "positive_review_count": pos_count,
                "negative_review_count": neg_count,
                "neutral_review_count": len(neu_list),
                "headline": headline,
                "status": "detected",
                "divergence_analysis": divergence_analysis,
                "evidence_items": evidence_items
            })

        logger.info(f"Detected {len(conflict_groups)} aspect conflicts for product {product_id}.")
        return conflict_groups

    def _analyze_contextual_divergence(
        self,
        pos_list: List[Dict[str, Any]],
        neg_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compares hardware variants and customer profiles between positive and negative cohorts."""
        pos_variants = [p.get("variant") for p in pos_list if p.get("variant")]
        neg_variants = [n.get("variant") for n in neg_list if n.get("variant")]

        pos_intensity = [p["context"].get("usage_intensity") for p in pos_list if p.get("context")]
        neg_intensity = [n["context"].get("usage_intensity") for n in neg_list if n.get("context")]

        pos_usecases = [p["context"].get("primary_use_case") for p in pos_list if p.get("context")]
        neg_usecases = [n["context"].get("primary_use_case") for n in neg_list if n.get("context")]

        hypotheses = []

        # Check variant divergence
        if pos_variants and neg_variants and set(pos_variants) != set(neg_variants):
            hypotheses.append({
                "dimension": "product_variant",
                "finding": f"Positive reviews frequently associate with '{pos_variants[0]}', while negative reviews cite '{neg_variants[0]}'."
            })

        # Check workload intensity divergence
        high_in_neg = neg_intensity.count("high")
        low_in_pos = pos_intensity.count("low")
        if high_in_neg > 0 and low_in_pos > 0:
            hypotheses.append({
                "dimension": "usage_intensity",
                "finding": "Dissatisfied customers predominantly report high-intensity workloads, whereas satisfied reviewers describe lightweight tasks."
            })

        # Check use case divergence
        if pos_usecases and neg_usecases:
            hypotheses.append({
                "dimension": "primary_use_case",
                "finding": f"Satisfied users highlight '{pos_usecases[0]}', whereas negative feedback aligns with '{neg_usecases[0]}'."
            })

        return {
            "has_contextual_divergence": len(hypotheses) > 0,
            "hypotheses": hypotheses,
            "pos_sample_count": len(pos_list),
            "neg_sample_count": len(neg_list)
        }

conflict_engine = ConflictDetectionEngine()
