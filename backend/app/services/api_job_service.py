from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ApiJob, ApiRateLimitSetting
from app.services.smartstore_upload_service import upload_master_product


DEFAULT_RATE_LIMITS = {
    "smartstore": {"max_per_minute": 30, "min_interval_seconds": 2},
    "gmarket": {"max_per_minute": 20, "min_interval_seconds": 3},
    "auction": {"max_per_minute": 20, "min_interval_seconds": 3},
    "elevenstreet": {"max_per_minute": 20, "min_interval_seconds": 3},
    "toss_shopping": {"max_per_minute": 20, "min_interval_seconds": 3},
    "coupang": {"max_per_minute": 20, "min_interval_seconds": 3},
    "lotteon": {"max_per_minute": 20, "min_interval_seconds": 3},
    "supplier": {"max_per_minute": 30, "min_interval_seconds": 2},
}


def ensure_default_rate_limits(db: Session) -> None:
    for service_name, defaults in DEFAULT_RATE_LIMITS.items():
        setting = db.scalar(select(ApiRateLimitSetting).where(ApiRateLimitSetting.service_name == service_name))
        if setting is None:
            db.add(ApiRateLimitSetting(service_name=service_name, **defaults))
    db.commit()


def enqueue_api_job(
    db: Session,
    service_name: str,
    job_type: str,
    related_entity_type: str,
    related_entity_id: int,
    payload_json: dict | None = None,
    priority: int = 100,
) -> ApiJob:
    dedupe_key = f"{service_name}:{job_type}:{related_entity_type}:{related_entity_id}"
    existing = db.scalar(select(ApiJob).where(ApiJob.dedupe_key == dedupe_key))
    if existing:
        existing.payload_json = payload_json or existing.payload_json
        existing.priority = min(existing.priority, priority)
        existing.status = "pending"
        existing.last_error_message = None
        existing.scheduled_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    job = ApiJob(
        service_name=service_name,
        job_type=job_type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        dedupe_key=dedupe_key,
        payload_json=payload_json,
        priority=priority,
        status="pending",
        scheduled_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_api_jobs(db: Session, status: str | None = None, service_name: str | None = None) -> list[ApiJob]:
    query = select(ApiJob).order_by(ApiJob.priority.asc(), ApiJob.scheduled_at.asc(), ApiJob.id.asc())
    if status:
        query = query.where(ApiJob.status == status)
    if service_name:
        query = query.where(ApiJob.service_name == service_name)
    return list(db.scalars(query).all())


def list_rate_limits(db: Session) -> list[ApiRateLimitSetting]:
    ensure_default_rate_limits(db)
    return list(db.scalars(select(ApiRateLimitSetting).order_by(ApiRateLimitSetting.service_name)).all())


def summarize_api_jobs(db: Session) -> dict:
    jobs = list(db.scalars(select(ApiJob)).all())
    by_status: dict[str, int] = {}
    by_service: dict[str, int] = {}
    failures: list[dict] = []

    for job in jobs:
        by_status[job.status] = by_status.get(job.status, 0) + 1
        by_service[job.service_name] = by_service.get(job.service_name, 0) + 1
        if job.status in {"failed", "retrying"} or job.last_error_message:
            failures.append(
                {
                    "id": job.id,
                    "service_name": job.service_name,
                    "job_type": job.job_type,
                    "related_entity_type": job.related_entity_type,
                    "related_entity_id": job.related_entity_id,
                    "status": job.status,
                    "attempt_count": job.attempt_count,
                    "max_attempt_count": job.max_attempt_count,
                    "last_error_message": job.last_error_message,
                    "scheduled_at": str(job.scheduled_at),
                }
            )

    return {
        "total": len(jobs),
        "by_status": by_status,
        "by_service": by_service,
        "failures": failures[:100],
    }


def retry_api_job_now(db: Session, api_job_id: int) -> ApiJob:
    job = db.get(ApiJob, api_job_id)
    if job is None:
        raise ValueError("api job not found")
    job.status = "pending"
    job.scheduled_at = datetime.now(timezone.utc)
    job.last_error_message = None
    db.commit()
    db.refresh(job)
    return job


def cancel_api_job(db: Session, api_job_id: int) -> ApiJob:
    job = db.get(ApiJob, api_job_id)
    if job is None:
        raise ValueError("api job not found")
    if job.status == "running":
        raise ValueError("running job cannot be cancelled")
    job.status = "cancelled"
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job


def run_pending_api_jobs(db: Session, limit: int = 10) -> dict:
    ensure_default_rate_limits(db)
    now = datetime.now(timezone.utc)
    jobs = list(
        db.scalars(
            select(ApiJob)
            .where(ApiJob.status.in_(["pending", "retrying"]))
            .where(ApiJob.scheduled_at <= now)
            .order_by(ApiJob.priority.asc(), ApiJob.scheduled_at.asc(), ApiJob.id.asc())
            .limit(limit)
        ).all()
    )

    result = {"picked": len(jobs), "done": 0, "failed": 0, "retrying": 0, "skipped": 0, "items": []}
    for job in jobs:
        if not _can_run_now(db, job, now):
            result["skipped"] += 1
            result["items"].append({"api_job_id": job.id, "status": "skipped", "reason": "rate_limited"})
            continue

        try:
            _run_single_job(db, job)
        except Exception as exc:  # noqa: BLE001 - worker must record every failure.
            _mark_failed_or_retrying(db, job, str(exc))
        else:
            result["done"] += 1
            result["items"].append({"api_job_id": job.id, "status": "done"})
            continue

        if job.status == "retrying":
            result["retrying"] += 1
        else:
            result["failed"] += 1
        result["items"].append({"api_job_id": job.id, "status": job.status, "error": job.last_error_message})

    return result


def _run_single_job(db: Session, job: ApiJob) -> None:
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    job.attempt_count += 1
    db.commit()

    if job.service_name == "smartstore" and job.job_type == "product_upload":
        master_product_id = int((job.payload_json or {}).get("master_product_id") or job.related_entity_id)
        upload_master_product(db, master_product_id)
    else:
        raise ValueError(f"Unsupported API job: {job.service_name}/{job.job_type}")

    job.status = "done"
    job.finished_at = datetime.now(timezone.utc)
    job.last_error_message = None
    db.commit()


def _mark_failed_or_retrying(db: Session, job: ApiJob, error_message: str) -> None:
    job.finished_at = datetime.now(timezone.utc)
    job.last_error_message = error_message[:2000]
    if job.attempt_count < job.max_attempt_count:
        job.status = "retrying"
        job.scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    else:
        job.status = "failed"
    db.commit()


def _can_run_now(db: Session, job: ApiJob, now: datetime) -> bool:
    setting = db.scalar(select(ApiRateLimitSetting).where(ApiRateLimitSetting.service_name == job.service_name))
    if setting is None or not setting.is_active:
        return True

    latest_finished = db.scalar(
        select(ApiJob.finished_at)
        .where(ApiJob.service_name == job.service_name)
        .where(ApiJob.finished_at.is_not(None))
        .order_by(ApiJob.finished_at.desc())
        .limit(1)
    )
    if latest_finished is None:
        latest_finished_ok = True
    else:
        if latest_finished.tzinfo is None:
            latest_finished = latest_finished.replace(tzinfo=timezone.utc)
        latest_finished_ok = latest_finished + timedelta(seconds=setting.min_interval_seconds) <= now

    one_minute_ago = now - timedelta(minutes=1)
    recent_finished_count = len(
        db.scalars(
            select(ApiJob.id)
            .where(ApiJob.service_name == job.service_name)
            .where(ApiJob.finished_at.is_not(None))
            .where(ApiJob.finished_at >= one_minute_ago)
        ).all()
    )
    return latest_finished_ok and recent_finished_count < setting.max_per_minute
