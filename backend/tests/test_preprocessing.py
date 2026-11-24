"""Tests for Text Preprocessing and Sanitization"""
from backend.ai.preprocessing import preprocessor


def test_clean_text_removes_html_and_urls():
    raw = "Great battery! <a href='https://spam.com'>Click here</a> http://example.com for more."
    cleaned = preprocessor.clean_text(raw)
    assert "<a href=" not in cleaned
    assert "https://spam.com" not in cleaned
    assert "Great battery!" in cleaned

def test_is_spam_or_invalid():
    # Too short
    is_spam, reason = preprocessor.is_spam_or_invalid("Short")
    assert is_spam is True

    # Repetitive gibberish
    is_spam, reason = preprocessor.is_spam_or_invalid("sooooooooo gooooooood aaaaaaaa")
    assert is_spam is True

    # Valid review
    is_spam, reason = preprocessor.is_spam_or_invalid("This laptop has been wonderful for my daily tasks.")
    assert is_spam is False

def test_segment_sentences():
    text = "Battery backup is amazing. However, the fan noise is loud under heavy gaming! Overall a good machine."
    segments = preprocessor.segment_sentences(text)
    assert len(segments) == 3
    assert "Battery backup is amazing" in segments[0]["sentence"]
    assert "fan noise is loud" in segments[1]["sentence"]
