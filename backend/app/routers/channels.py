from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ChannelProductProfile, ErrorQueue
from app.services.api_job_service import enqueue_api_job
from app.services.channel_profile_service import ensure_channel_profile, list_channel_profiles, save_validation_result
from app.services.channel_validation import get_required_attributes, validate_channel_profile
from app.services.inventory_sync import sync_inventory as run_inventory_sync
from app.services.smartstore_upload_service import build_payload_for_master, upload_master_product
from app.services.smartstore_validation import validate_master_for_smartstore

router = APIRouter(tags=["channels"])


class ChannelProductProfileUpdate(BaseModel):
    channel_product_name: str | None = None
    channel_category_id: str | None = None
    channel_sale_price: int | None = None
    channel_shipping_fee: int | None = None
    channel_attributes_json: dict | None = None
    channel_status: str | None = None
    use_master_name: bool | None = None
    use_master_price: bool | None = None
    use_master_images: bool | None = None


@router.post("/channels/smartstore/products/{master_product_id}/build-payload")
def build_smartstore_payload(master_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return build_payload_for_master(db, master_product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/channels/smartstore/products/{master_product_id}/validate")
def validate_smartstore_product(master_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        result = validate_master_for_smartstore(db, master_product_id)
        save_validation_result(db, "smartstore", master_product_id, result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/channels/smartstore/products/{master_product_id}/upload")
def upload_smartstore_product(master_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        channel_product = upload_master_product(db, master_product_id)
    except ValueError as exc:
        status_code = 422 if "validation" in str(exc) else 404
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return {
        "status": "ok",
        "channel_product_id": channel_product.id,
        "smartstore_product_id": channel_product.channel_product_id,
        "channel_status": channel_product.channel_status,
    }


@router.post("/channels/smartstore/products/{master_product_id}/enqueue-upload")
def enqueue_smartstore_upload(master_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        validation = validate_master_for_smartstore(db, master_product_id)
        save_validation_result(db, "smartstore", master_product_id, validation)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not validation["valid"]:
        raise HTTPException(status_code=422, detail={"message": "validation failed", "validation": validation})

    job = enqueue_api_job(
        db=db,
        service_name="smartstore",
        job_type="product_upload",
        related_entity_type="master_product",
        related_entity_id=master_product_id,
        payload_json={"master_product_id": master_product_id},
        priority=50,
    )
    return {"status": "queued", "api_job_id": job.id, "dedupe_key": job.dedupe_key}


@router.get("/channels/product-profiles")
def get_channel_product_profiles(channel_code: str | None = None, db: Session = Depends(get_db)) -> dict:
    profiles = list_channel_profiles(db, channel_code)
    return {
        "items": [
            {
                "id": profile.id,
                "channel_id": profile.channel_id,
                "channel_code": profile.channel.code,
                "channel_name": profile.channel.name,
                "master_product_id": profile.master_product_id,
                "internal_product_code": profile.master_product.internal_product_code,
                "master_product_name": profile.master_product.cleaned_name or profile.master_product.product_name,
                "channel_product_name": profile.channel_product_name,
                "channel_category_id": profile.channel_category_id,
                "channel_sale_price": profile.channel_sale_price,
                "channel_shipping_fee": profile.channel_shipping_fee,
                "channel_attributes_json": profile.channel_attributes_json or {},
                "channel_status": profile.channel_status,
                "use_master_name": profile.use_master_name,
                "use_master_price": profile.use_master_price,
                "use_master_images": profile.use_master_images,
                "upload_validation_status": profile.upload_validation_status,
                "last_validation_json": profile.last_validation_json,
            }
            for profile in profiles
        ]
    }


@router.post("/channels/{channel_code}/products/{master_product_id}/prepare-profile")
def prepare_channel_product_profile(channel_code: str, master_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        profile = ensure_channel_profile(db, channel_code, master_product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"status": "ok", "channel_product_profile_id": profile.id}


@router.patch("/channels/product-profiles/{profile_id}")
def update_channel_product_profile(
    profile_id: int,
    payload: ChannelProductProfileUpdate,
    db: Session = Depends(get_db),
) -> dict:
    profile = db.get(ChannelProductProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="channel product profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return {"status": "ok", "channel_product_profile_id": profile.id}


@router.get("/channels/{channel_code}/required-attributes")
def get_channel_required_attributes(channel_code: str) -> dict:
    return get_required_attributes(channel_code)


@router.post("/channels/product-profiles/{profile_id}/validate")
def validate_channel_product_profile(profile_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        return validate_channel_profile(db, profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/inventory/sync")
def sync_inventory(db: Session = Depends(get_db)) -> dict:
    result = run_inventory_sync(db)
    return {"status": "ok", **result}


@router.get("/channels/smartstore/upload-failures")
def list_smartstore_upload_failures(db: Session = Depends(get_db)) -> dict:
    failures = db.scalars(
        select(ErrorQueue)
        .where(ErrorQueue.task_type == "smartstore_upload_validation")
        .order_by(ErrorQueue.id.desc())
    ).all()
    return {
        "items": [
            {
                "id": failure.id,
                "master_product_id": failure.related_entity_id,
                "error_message": failure.error_message,
                "retry_count": failure.retry_count,
                "status": failure.status,
                "created_at": str(failure.created_at),
            }
            for failure in failures
        ]
    }
