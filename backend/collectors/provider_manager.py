"""Provider Manager: Multi-source Orchestrator with Deduplication and Fallback"""
from typing import List, Dict, Any, Optional
from backend.collectors.base import BaseReviewCollector
from backend.collectors.curated_dataset import CuratedDatasetCollector
from backend.collectors.amazon import AmazonCollector
from backend.collectors.flipkart import FlipkartCollector
from backend.schemas.review import ReviewNormalizationResult
from backend.core.logging import logger
from backend.core.config import settings


class ProviderManager:
    """
    Orchestrates review providers, unifies product discovery,
    normalizes external review schemas, and ensures zero duplication.
    """
    def __init__(self):
        self.providers: Dict[str, BaseReviewCollector] = {
            "curated": CuratedDatasetCollector(),
            "amazon": AmazonCollector(),
            "flipkart": FlipkartCollector()
        }

    def search_all_sources(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Searches across all registered collectors and aggregates unique products."""
        aggregated: Dict[str, Dict[str, Any]] = {}
        for name, collector in self.providers.items():
            try:
                results = collector.search_products(query, limit=limit)
                for item in results:
                    key = item.get("title", "").strip().lower()
                    if key not in aggregated:
                        aggregated[key] = item
                        aggregated[key]["available_sources"] = [collector.source_name]
                    else:
                        if collector.source_name not in aggregated[key]["available_sources"]:
                            aggregated[key]["available_sources"].append(collector.source_name)
            except Exception as e:
                logger.error(f"Error querying provider {name}: {e}")
        
        return list(aggregated.values())[:limit]

    def collect_reviews_for_product(
        self,
        external_id: str,
        preferred_provider: Optional[str] = "all",
        limit_per_provider: int = 50
    ) -> List[ReviewNormalizationResult]:
        """
        Collects normalized reviews from specified providers with automatic cross-provider deduplication.
        """
        all_normalized: List[ReviewNormalizationResult] = []
        global_seen_hashes: set = set()

        providers_to_query = (
            [self.providers[preferred_provider]]
            if preferred_provider in self.providers
            else list(self.providers.values())
        )

        for collector in providers_to_query:
            try:
                raw_reviews = collector.fetch_reviews(external_id, limit=limit_per_provider)
                for raw in raw_reviews:
                    norm = collector.normalize_review(raw)
                    if norm:
                        h = collector.compute_review_hash(norm.review_text, norm.reviewer_name)
                        if h not in global_seen_hashes:
                            global_seen_hashes.add(h)
                            all_normalized.append(norm)
            except Exception as e:
                logger.error(f"Error collecting reviews via {collector.source_name}: {e}")

        logger.info(f"Aggregated {len(all_normalized)} verified reviews for '{external_id}'.")
        return all_normalized

provider_manager = ProviderManager()
