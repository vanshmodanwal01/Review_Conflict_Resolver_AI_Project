"""Abstract Base Collector for Permitted Review Data Sources"""
import time
import abc
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import ValidationError
from backend.schemas.review import ReviewNormalizationResult
from backend.core.logging import logger
from backend.core.config import settings


class RateLimiter:
    """Token bucket / sliding window rate limiter."""
    def __init__(self, max_requests_per_minute: int = 30):
        self.max_requests = max_requests_per_minute
        self.interval = 60.0
        self.timestamps: List[float] = []

    def acquire(self):
        now = time.time()
        # Evict timestamps older than 60 seconds
        self.timestamps = [ts for ts in self.timestamps if now - ts < self.interval]
        if len(self.timestamps) >= self.max_requests:
            sleep_time = self.interval - (now - self.timestamps[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Throttling for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
        self.timestamps.append(time.time())


class BaseReviewCollector(abc.ABC):
    """
    Abstract Base Class for all review data providers.
    Enforces normalization, error handling, rate limiting, and zero bypass of access controls.
    """
    def __init__(self, source_name: str, base_url: Optional[str] = None):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)
        self.seen_review_hashes: set = set()

    @abc.abstractmethod
    def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products on the external source or catalog."""
        pass

    @abc.abstractmethod
    def fetch_reviews(self, external_product_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch raw review objects for a product."""
        pass

    def compute_review_hash(self, text: str, reviewer: Optional[str] = None) -> str:
        """Computes deterministic hash for duplicate detection."""
        normalized_str = f"{text.strip().lower()}:{reviewer or ''}"
        return hashlib.sha256(normalized_str.encode('utf-8')).hexdigest()

    def is_duplicate(self, text: str, reviewer: Optional[str] = None) -> bool:
        """Returns True if this exact review was already processed."""
        r_hash = self.compute_review_hash(text, reviewer)
        if r_hash in self.seen_review_hashes:
            return True
        self.seen_review_hashes.add(r_hash)
        return False

    def normalize_review(self, raw_data: Dict[str, Any]) -> Optional[ReviewNormalizationResult]:
        """
        Transforms raw provider dictionary into normalized ReviewNormalizationResult schema.
        Preserves original raw data.
        """
        try:
            text = str(raw_data.get("review_text", "")).strip()
            if not text or len(text) < 3:
                return None

            reviewer = raw_data.get("reviewer_name")
            if self.is_duplicate(text, reviewer):
                logger.debug(f"Duplicate review detected and filtered: {text[:40]}...")
                return None

            rating = float(raw_data.get("rating", 3.0))
            # Clamp rating between 1.0 and 5.0
            rating = max(1.0, min(5.0, rating))

            norm = ReviewNormalizationResult(
                source=self.source_name,
                external_product_id=str(raw_data.get("external_product_id", "")),
                product_name=str(raw_data.get("product_name", "")),
                rating=rating,
                review_text=text,
                variant=raw_data.get("variant"),
                review_date=raw_data.get("review_date", datetime.now(timezone.utc).isoformat()),
                reviewer_name=reviewer,
                verified_purchase=bool(raw_data.get("verified_purchase", True))
            )
            return norm
        except (ValidationError, Exception) as e:
            logger.error(f"Error normalizing review from {self.source_name}: {e}")
            return None
