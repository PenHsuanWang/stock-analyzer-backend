"""
FastAPI router for scheduler endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, validator
from typing import List, Optional
import re

from webapp.serving_app.scheduler_serving_app import (
    SchedulerServingApp,
    get_scheduler_app
)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


# Request/Response Models
class CreateJobRequest(BaseModel):
    """Request model for creating a scheduled job."""
    name: str
    stock_ids: List[str]
    schedule_time: str = "17:00"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prefix: str = "scheduled_stock_data"
    
    @validator('schedule_time')
    def validate_time_format(cls, v):
        """Validate time format."""
        if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', v):
            raise ValueError('Invalid time format. Use HH:MM')
        return v
    
    @validator('stock_ids')
    def validate_stock_ids(cls, v):
        """Validate stock IDs."""
        if not v:
            raise ValueError('At least one stock ID is required')
        return v


class UpdateJobRequest(BaseModel):
    """Request model for updating a job."""
    name: Optional[str] = None
    stock_ids: Optional[List[str]] = None
    schedule_time: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    """Response model for job details."""
    job_id: str
    name: str
    stock_ids: List[str]
    schedule_time: str
    is_active: bool
    status: str
    created_at: str
    last_run: Optional[str]
    next_run: Optional[str]


# Endpoints
@router.post("/jobs", response_model=dict)
def create_job(
    request: CreateJobRequest = Body(...),
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """
    Create a new scheduled job.
    
    The job will automatically run daily at the specified time.
    """
    try:
        job_id = app.create_job(
            name=request.name,
            stock_ids=request.stock_ids,
            schedule_time=request.schedule_time,
            start_date=request.start_date,
            end_date=request.end_date,
            prefix=request.prefix
        )
        return {
            "message": "Job created successfully",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=List[dict])
def list_jobs(
    active_only: bool = False,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """
    List all scheduled jobs.
    
    Query Parameters:
        active_only: If true, return only active jobs
    """
    return app.list_jobs(active_only=active_only)


@router.get("/jobs/{job_id}", response_model=dict)
def get_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Get details of a specific job."""
    job = app.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/jobs/{job_id}", response_model=dict)
def update_job(
    job_id: str,
    request: UpdateJobRequest = Body(...),
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Update an existing job."""
    success = app.update_job(
        job_id=job_id,
        name=request.name,
        stock_ids=request.stock_ids,
        schedule_time=request.schedule_time,
        start_date=request.start_date,
        end_date=request.end_date,
        is_active=request.is_active
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job updated successfully"}


@router.delete("/jobs/{job_id}", response_model=dict)
def delete_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Delete a scheduled job."""
    success = app.delete_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


@router.post("/jobs/{job_id}/start", response_model=dict)
def start_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Activate a job to start running on schedule."""
    success = app.start_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job started successfully"}


@router.post("/jobs/{job_id}/stop", response_model=dict)
def stop_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Deactivate a job to stop it from running."""
    success = app.stop_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job stopped successfully"}


@router.get("/status", response_model=dict)
def get_scheduler_status(
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Get scheduler status and statistics."""
    return app.get_scheduler_status()
