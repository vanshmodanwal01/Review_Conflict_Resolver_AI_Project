"""Tests for Collectors and Normalization"""
from backend.collectors.curated_dataset import CuratedDatasetCollector
from backend.collectors.provider_manager import provider_manager


def test_curated_collector_search_and_fetch():
    collector = CuratedDatasetCollector()
    results = collector.search_products("Dell XPS")
    assert len(results) >= 1
    assert "Dell XPS 15" in results[0]["title"]

    reviews = collector.fetch_reviews(results[0]["external_id"])
    assert len(reviews) >= 4
    for r in reviews:
        assert "rating" in r
        assert "review_text" in r
        assert r["source"] == "Curated Verified Dataset"

def test_duplicate_filtering():
    collector = CuratedDatasetCollector()
    raw = {
        "source": "Test",
        "external_product_id": "P1",
        "product_name": "Test Laptop",
        "rating": 4.0,
        "review_text": "Identical review string for duplicate detection check.",
        "reviewer_name": "Alice"
    }
    norm1 = collector.normalize_review(raw)
    assert norm1 is not None

    # Second submission must be filtered as duplicate
    norm2 = collector.normalize_review(raw)
    assert norm2 is None
