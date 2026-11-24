"""Tests for Aspect-Based Sentiment Analysis (ABSA)"""
from backend.ai.aspect_extractor import aspect_extractor


def test_aspect_extraction_deconstructs_multiple_aspects():
    review = "The laptop speed and multitasking is fantastic, but battery backup is disappointing and dies fast."
    aspects = aspect_extractor.extract_aspects(review)
    assert len(aspects) >= 2

    asp_map = {a["aspect_category"]: a for a in aspects}
    assert "performance" in asp_map
    assert asp_map["performance"]["sentiment"] == "positive"
    assert asp_map["performance"]["sentiment_score"] > 0

    assert "battery" in asp_map
    assert asp_map["battery"]["sentiment"] == "negative"
    assert asp_map["battery"]["sentiment_score"] < 0

def test_thermals_and_display_detection():
    review = "Fans sound like a jet engine and the OLED screen is gorgeous."
    aspects = aspect_extractor.extract_aspects(review)
    asp_map = {a["aspect_category"]: a for a in aspects}
    
    assert "thermals_and_noise" in asp_map
    assert asp_map["thermals_and_noise"]["sentiment"] == "negative"
    assert "display" in asp_map
    assert asp_map["display"]["sentiment"] == "positive"
