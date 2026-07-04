from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.api_job_service import (
    cancel_api_job,
    list_api_jobs,
    list_rate_limits,
    retry_api_job_now,
    run_pending_api_jobs,
    summarize_api_jobs,
)

router = APIRouter(tags=["api-jobs"])


@router.get("/api-jobs")
def get_api_jobs(
    status: str | None = None,
    service_name: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    jobs = list_api_jobs(db, status=status, service_name=service_name)
    return {
        "items": [
            {
                "id": job.id,
                "service_name": job.service_name,
                "job_type": job.job_type,
                "related_entity_type": job.related_entity_type,
                "related_entity_id": job.related_entity_id,
                "status": job.status,
                "priority": job.priority,
                "attempt_count": job.attempt_count,
                "scheduled_at": str(job.scheduled_at),
                "last_error_message": job.last_error_message,
            }
            for job in jobs
        ]
    }


@router.get("/settings/api-rate-limits")
def get_api_rate_limits(db: Session = Depends(get_db)) -> dict:
    settings = list_rate_limits(db)
    return {
        "items": [
            {
                "service_name": setting.service_name,
                "max_per_minute": setting.max_per_minute,
                "min_interval_seconds": setting.min_interval_seconds,
                "is_active": setting.is_active,
            }
            for setting in settings
        ]
    }


@router.post("/api-jobs/run-pending")
def run_api_jobs(limit: int = 10, db: Session = Depends(get_db)) -> dict:
    return run_pending_api_jobs(db, limit=limit)


@router.get("/api-jobs/summary")
def get_api_jobs_summary(db: Session = Depends(get_db)) -> dict:
    return summarize_api_jobs(db)


@router.post("/api-jobs/{api_job_id}/retry-now")
def retry_api_job(api_job_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        job = retry_api_job_now(db, api_job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "api_job_id": job.id, "job_status": job.status}


@router.post("/api-jobs/{api_job_id}/cancel")
def cancel_job(api_job_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        job = cancel_api_job(db, api_job_id)
    except ValueError as exc:
        status_code = 409 if "running" in str(exc) else 404
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return {"status": "ok", "api_job_id": job.id, "job_status": job.status}
