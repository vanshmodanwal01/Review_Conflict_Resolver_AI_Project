"""Analysis Execution and Summary Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from backend.api.deps import DbSession
from backend.services.analysis_service import AnalysisService, analysis_service
from backend.services.product_service import ProductService
from backend.models.analysis import AnalysisJob
from backend.schemas.analysis import (
    AnalysisTriggerRequest,
    AnalysisJobResponse,
    ProductAnalysisSummaryResponse
)


router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/{product_id}", response_model=AnalysisJobResponse)
async def trigger_analysis(
    product_id: str,
    request: AnalysisTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = DbSession
):
    """
    Triggers end-to-end review aspect analysis, conflict detection, and explanation generation.
    Returns immediately with a trackable job_id.
    """
    product = ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Create Job record
    job = AnalysisJob(
        product_id=product_id,
        status="pending",
        progress_percent=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Schedule task in background or execute directly
    background_tasks.add_task(
        analysis_service.process_product_analysis,
        db=db,
        product_id=product_id,
        job_id=job.id,
        force_refresh=request.force_refresh
    )

    return AnalysisJobResponse(
        job_id=job.id,
        product_id=job.product_id,
        status=job.status,
        progress_percent=job.progress_percent,
        total_reviews=job.total_reviews,
        processed_reviews=job.processed_reviews,
        detected_conflicts=job.detected_conflicts,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at
    )

@router.get("/summary/{product_id}", response_model=ProductAnalysisSummaryResponse)
def get_product_analysis_summary(product_id: str, db: Session = DbSession):
    """Returns overview statistics, rating/sentiment distribution, and aspect breakdown."""
    summary = AnalysisService.get_analysis_summary(db, product_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product analysis not found")
    return summary

@router.get("/job/{job_id}", response_model=AnalysisJobResponse)
def get_job_status(job_id: str, db: Session = DbSession):
    """Monitors asynchronous analysis execution status."""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis job not found")
    return AnalysisJobResponse(
        job_id=job.id,
        product_id=job.product_id,
        status=job.status,
        progress_percent=job.progress_percent,
        total_reviews=job.total_reviews,
        processed_reviews=job.processed_reviews,
        detected_conflicts=job.detected_conflicts,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at
    )
