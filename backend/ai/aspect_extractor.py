"""Aspect-Based Sentiment Analysis (ABSA) Engine for Laptops"""
import re
from typing import List, Dict, Any, Optional, Tuple
from backend.ai.preprocessing import preprocessor
from backend.core.logging import logger


ASPECT_KEYWORDS = {
    "battery": [
        "battery life", "battery backup", "battery", "backup", "charger", "charging",
        "power brick", "endurance", "unplugged", "discharge"
    ],
    "performance": [
        "performance", "speed", "responsiveness", "snappy", "multitasking", "boot time",
        "processor", "cpu", "ram", "gpu", "rendering", "exporting", "fps", "frame rate"
    ],
    "thermals_and_noise": [
        "thermal", "thermals", "heat", "heating", "cooling", "fan noise", "fan", "fans",
        "temperature", "temperatures", "noise", "throttle", "throttling"
    ],
    "display": [
        "display", "screen", "panel", "oled", "ips", "brightness", "nits", "glare",
        "reflection", "contrast", "resolution", "refresh rate", "color accuracy", "viewing angle"
    ],
    "build_quality": [
        "build quality", "build", "hinge", "hinges", "chassis", "aluminum", "flex",
        "durability", "sturdiness", "weight", "portability"
    ],
    "keyboard_and_trackpad": [
        "keyboard", "keys", "key travel", "typing feel", "typing", "trackpad", "touchpad",
        "backlight", "numpad"
    ],
    "audio_and_webcam": [
        "speakers", "speaker", "audio", "sound quality", "webcam", "camera", "microphone", "mic"
    ],
    "value_for_money": [
        "value for money", "price to performance", "pricing", "price tag", "cost"
    ]
}

POSITIVE_TERMS = {
    "excellent", "great", "amazing", "superb", "fantastic", "outstanding", "impressive",
    "best", "love", "good", "fast", "smooth", "silent", "cool", "sharp", "vivid", "crisp",
    "long", "lasts", "sturdy", "premium", "delight", "flawless", "magic", "snappy", "durable",
    "gorgeous", "brilliant", "stunning", "beautiful", "responsive", "quiet", "buttery", "sleek",
    "sharp", "top-notch"
}

NEGATIVE_TERMS = {
    "terrible", "horrible", "awful", "bad", "poor", "disappointing", "disappointed",
    "disaster", "barely", "drains", "drain", "slow", "lag", "lags", "stutter", "stutters",
    "hot", "burning", "noisy", "loud", "throttle", "throttles", "throttling", "mirror",
    "glare", "cheap", "creak", "flex", "overpriced", "cramped", "worst", "hate", "issue",
    "problem", "dies", "die", "jet engine"
}

NEGATION_TERMS = {"not", "never", "no", "barely", "hardly", "doesn't", "don't", "isn't", "wasn't"}

# Sub-clause and compound separators: e.g. "but", "however", "and the", "and it"
SUB_CLAUSE_REGEX = re.compile(
    r';|\b(?:but|however|although|though|whereas|while|yet|and yet|on the other hand|and\s+(?:the|it|this|that|its))\b',
    re.IGNORECASE
)


class AspectExtractor:
    """
    Extracts fine-grained product aspects, assigns polarities, and preserves exact evidence snippets.
    Uses sub-clause segmentation and targeted window analysis for accurate aspect sentiment attribution.
    """
    def __init__(self):
        self.aspect_tax = ASPECT_KEYWORDS

    def analyze_text_sentiment(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        pos_hits = sum(1 for w in words if w in POSITIVE_TERMS)
        neg_hits = sum(1 for w in words if w in NEGATIVE_TERMS)
        
        if "jet engine" in text_lower:
            neg_hits += 2

        has_negation = any(w in NEGATION_TERMS for w in words)

        raw_score = 0.0
        total_hits = pos_hits + neg_hits
        if total_hits > 0:
            raw_score = (pos_hits - neg_hits) / total_hits
            if has_negation:
                raw_score = -raw_score

        if raw_score >= 0.15:
            sentiment = "positive"
        elif raw_score <= -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return sentiment, raw_score

    def extract_aspects(self, review_text: str) -> List[Dict[str, Any]]:
        sentences = preprocessor.segment_sentences(review_text)
        detected_aspects = []

        for sent in sentences:
            sent_str = sent["sentence"]
            # Split into sub-clauses
            raw_clauses = SUB_CLAUSE_REGEX.split(sent_str)
            clauses = [c.strip() for c in raw_clauses if c.strip()]
            if not clauses:
                clauses = [sent_str]

            for aspect_name, keywords in self.aspect_tax.items():
                for kw in keywords:
                    pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                    
                    matched_clause = None
                    for cl in clauses:
                        if pattern.search(cl):
                            matched_clause = cl
                            break
                    
                    if matched_clause:
                        sentiment, score = self.analyze_text_sentiment(matched_clause)
                        # If sub-clause was neutral, fallback to full sentence sentiment
                        if sentiment == "neutral":
                            sent_sentiment, sent_score = self.analyze_text_sentiment(sent_str)
                            if sent_sentiment != "neutral":
                                sentiment, score = sent_sentiment, sent_score

                        already = any(
                            da["aspect_category"] == aspect_name and da["char_start"] == sent["start"]
                            for da in detected_aspects
                        )
                        if not already:
                            detected_aspects.append({
                                "aspect_category": aspect_name,
                                "sentiment": sentiment,
                                "sentiment_score": round(score, 2),
                                "evidence_snippet": matched_clause,
                                "char_start": sent["start"],
                                "char_end": sent["end"],
                                "matched_keyword": kw
                            })
                        break

        return detected_aspects

aspect_extractor = AspectExtractor()
