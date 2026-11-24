"""Collectors Package Exports"""
from backend.collectors.base import BaseReviewCollector
from backend.collectors.curated_dataset import CuratedDatasetCollector
from backend.collectors.amazon import AmazonCollector
from backend.collectors.flipkart import FlipkartCollector
from backend.collectors.provider_manager import ProviderManager, provider_manager

__all__ = [
    "BaseReviewCollector",
    "CuratedDatasetCollector",
    "AmazonCollector",
    "FlipkartCollector",
    "ProviderManager",
    "provider_manager"
]
