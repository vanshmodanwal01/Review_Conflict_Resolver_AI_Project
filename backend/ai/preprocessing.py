"""Text Sanitization, Spam Detection, and Sentence Segmentation Preprocessor"""
import re
import html
from typing import List, Dict, Any, Tuple
from backend.core.logging import logger


# Common noise / spam regex patterns
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r'<.*?>')
EXCESS_WHITESPACE = re.compile(r'\s+')
MULTIPLE_PUNCTUATION = re.compile(r'([!?.]){2,}')
NON_ASCII_CLEANUP = re.compile(r'[^\x00-\x7F]+')


class TextPreprocessor:
    """
    Sanitizes, validates, and segments customer review text.
    Filters spam, normalizes whitespace, and extracts clean sentence segments.
    """
    @staticmethod
    def clean_text(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        
        # Unescape HTML entities
        cleaned = html.unescape(text)
        # Strip HTML tags
        cleaned = HTML_TAG_PATTERN.sub('', cleaned)
        # Strip URLs
        cleaned = URL_PATTERN.sub('', cleaned)
        # Normalize repeated punctuation (e.g., "!!!!" -> "!")
        cleaned = MULTIPLE_PUNCTUATION.sub(r'\1', cleaned)
        # Normalize whitespace
        cleaned = EXCESS_WHITESPACE.sub(' ', cleaned).strip()
        return cleaned

    @staticmethod
    def is_spam_or_invalid(text: str) -> Tuple[bool, str]:
        """Validates if review text is too short, gibberish, or spam."""
        if not text or len(text.strip()) < 10:
            return True, "Review text too short (under 10 chars)"
        
        # Word count check
        words = text.split()
        if len(words) < 3:
            return True, "Review text has fewer than 3 words"
        
        # Check repeated character gibberish (e.g. "aaaaaaa", "asdfasdfasdf")
        if re.search(r'(.)\1{5,}', text):
            return True, "Repetitive character gibberish detected"
            
        return False, "Valid"

    @staticmethod
    def segment_sentences(text: str) -> List[Dict[str, Any]]:
        """
        Splits review into individual sentences while recording character start & end spans.
        """
        cleaned = TextPreprocessor.clean_text(text)
        # Sentence splitting pattern (handles ., !, ? followed by space or capital letter)
        sentence_delimiters = re.compile(r'(?<=[.!?])\s+')
        raw_sentences = sentence_delimiters.split(cleaned)
        
        segments = []
        current_offset = 0
        for s in raw_sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            start = cleaned.find(s_clean, current_offset)
            end = start + len(s_clean)
            segments.append({
                "sentence": s_clean,
                "start": start if start != -1 else current_offset,
                "end": end if start != -1 else current_offset + len(s_clean)
            })
            if start != -1:
                current_offset = end
        
        return segments

preprocessor = TextPreprocessor()
