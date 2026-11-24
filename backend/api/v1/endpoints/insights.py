"""Personalized Insights and User Buying Advisory Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.api.deps import DbSession
from backend.services.conflict_service import ConflictService
from backend.schemas.insight import PersonalizedInsightRequest, PersonalizedInsightResponse


router = APIRouter(prefix="/insights", tags=["Insights"])

@router.post("/personalized", response_model=PersonalizedInsightResponse)
def get_personalized_insights(request: PersonalizedInsightRequest, db: Session = DbSession):
    """
    Evaluates buyer's planned use case, intensity, and variant preferences
    against detected review conflicts to deliver personalized expectation advisories.
    """
    res = ConflictService.get_personalized_advisory(db, request)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{request.product_id}' not found."
        )
    return res
