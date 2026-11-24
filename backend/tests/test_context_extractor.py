"""Tests for Context Extractor"""
from backend.ai.context_extractor import context_extractor


def test_extract_high_intensity_content_creation():
    review = "Terrible battery while editing 4K Premiere Pro timelines on 32GB RAM."
    ctx = context_extractor.extract_context(review)
    assert ctx["primary_use_case"] == "content_creation"
    assert ctx["usage_intensity"] == "high"
    assert ctx["extracted_attributes"].get("mentioned_ram") == "32GB"

def test_extract_low_intensity_office():
    review = "Lasts 10 hours easily during Zoom calls and spreadsheet editing."
    ctx = context_extractor.extract_context(review)
    assert ctx["primary_use_case"] == "office_work"
    assert ctx["usage_intensity"] == "low"

def test_benchmark_expectation_cues():
    review = "Trackpad is okay, but doesn't feel as responsive as my old MacBook."
    ctx = context_extractor.extract_context(review)
    assert "MacBook" in str(ctx["expectation_benchmark"])
