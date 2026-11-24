"""API v1 Central Router"""
from fastapi import APIRouter
from backend.api.v1.endpoints.products import router as products_router
from backend.api.v1.endpoints.reviews import router as reviews_router
from backend.api.v1.endpoints.analysis import router as analysis_router
from backend.api.v1.endpoints.conflicts import router as conflicts_router
from backend.api.v1.endpoints.insights import router as insights_router

api_v1_router = APIRouter()

api_v1_router.include_router(products_router)
api_v1_router.include_router(reviews_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(conflicts_router)
api_v1_router.include_router(insights_router)
