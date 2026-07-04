from sqlalchemy.orm import Session

from app.models import ApiLog


def create_api_log(
    db: Session,
    service_name: str,
    endpoint: str,
    method: str,
    request_json: dict | None,
    response_json: dict | None,
    status_code: int | None,
    success: bool,
    error_message: str | None = None,
) -> ApiLog:
    log = ApiLog(
        service_name=service_name,
        endpoint=endpoint,
        method=method,
        request_json=request_json,
        response_json=response_json,
        status_code=status_code,
        success=success,
        error_message=error_message,
    )
    db.add(log)
    return log
