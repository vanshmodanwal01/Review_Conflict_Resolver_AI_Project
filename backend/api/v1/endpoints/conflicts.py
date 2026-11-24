"""Conflict Explorer and Detailed Evidence Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.api.deps import DbSession
from backend.services.conflict_service import ConflictService
from backend.schemas.conflict import ConflictGroupSummary, ConflictGroupDetailResponse


router = APIRouter(prefix="/conflicts", tags=["Conflicts"])

@router.get("/{product_id}", response_model=List[ConflictGroupSummary])
def get_conflicts_for_product(product_id: str, db: Session = DbSession):
    """Retrieves all detected conflict groups for the specified product."""
    return ConflictService.get_conflicts_for_product(db, product_id)

@router.get("/details/{conflict_id}", response_model=ConflictGroupDetailResponse)
def get_conflict_details(conflict_id: str, db: Session = DbSession):
    """Retrieves forensic breakdown of a conflict, citing real customer review excerpts."""
    details = ConflictService.get_conflict_details(db, conflict_id)
    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict group not found")
    return details
