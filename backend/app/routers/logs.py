from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApiLog

router = APIRouter(tags=["logs"])


@router.get("/logs/api")
def list_api_logs(
    service_name: str | None = None,
    success: bool | None = None,
    db: Session = Depends(get_db),
) -> dict[str, list]:
    query = select(ApiLog).order_by(ApiLog.id.desc())
    if service_name:
        query = query.where(ApiLog.service_name == service_name)
    if success is not None:
        query = query.where(ApiLog.success == success)
    logs = db.scalars(query).all()
    return {
        "items": [
            {
                "id": log.id,
                "service_name": log.service_name,
                "endpoint": log.endpoint,
                "method": log.method,
                "status_code": log.status_code,
                "success": log.success,
                "error_message": log.error_message,
                "request_json": log.request_json,
                "response_json": log.response_json,
            }
            for log in logs
        ]
    }
