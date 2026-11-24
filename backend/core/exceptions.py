"""Custom Domain Exceptions for Review Conflict Resolver"""
from fastapi import HTTPException, status

class AppBaseException(Exception):
    """Base application exception."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ProductNotFoundError(AppBaseException):
    """Raised when a product is not found in database."""
    pass

class ReviewCollectionError(AppBaseException):
    """Raised when data collection encounters a non-recoverable error."""
    pass

class LLMProviderError(AppBaseException):
    """Raised when external LLM call fails or returns malformed response."""
    pass

class InsufficientEvidenceError(AppBaseException):
    """Raised when a conflict cannot be explained due to missing review context."""
    pass
