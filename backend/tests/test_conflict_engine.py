"""Tests for Conflict Detection Engine"""
from backend.ai.conflict_engine import conflict_engine


def test_detects_contradictory_battery_opinions():
    reviews = [
        {
            "id": "rev1",
            "rating": 5.0,
            "review_text": "Battery lasts 10 hours of light web browsing.",
            "variant": "FHD+ 16GB",
            "context": {"usage_intensity": "low", "primary_use_case": "office_work"},
            "aspects": [{"aspect_category": "battery", "sentiment": "positive", "sentiment_score": 0.8, "evidence_snippet": "lasts 10 hours"}]
        },
        {
            "id": "rev2",
            "rating": 1.0,
            "review_text": "Battery drains in 3 hours while playing games.",
            "variant": "4K OLED 32GB",
            "context": {"usage_intensity": "high", "primary_use_case": "gaming"},
            "aspects": [{"aspect_category": "battery", "sentiment": "negative", "sentiment_score": -0.8, "evidence_snippet": "drains in 3 hours"}]
        }
    ]
    conflicts = conflict_engine.detect_conflicts("prod-1", reviews)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c["aspect_category"] == "battery"
    assert c["positive_review_count"] == 1
    assert c["negative_review_count"] == 1
    assert c["conflict_score"] >= 0.5
    assert c["divergence_analysis"]["has_contextual_divergence"] is True

def test_does_not_flag_unrelated_aspects_as_conflict():
    reviews = [
        {
            "id": "rev1",
            "rating": 5.0,
            "review_text": "The camera and webcam are outstanding.",
            "aspects": [{"aspect_category": "audio_and_webcam", "sentiment": "positive", "sentiment_score": 0.9, "evidence_snippet": "webcam is outstanding"}]
        },
        {
            "id": "rev2",
            "rating": 2.0,
            "review_text": "Disappointed with battery life.",
            "aspects": [{"aspect_category": "battery", "sentiment": "negative", "sentiment_score": -0.7, "evidence_snippet": "Disappointed with battery"}]
        }
    ]
    conflicts = conflict_engine.detect_conflicts("prod-2", reviews)
    # Different aspects must never be flagged as contradictory
    assert len(conflicts) == 0
