from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Channel,
    ChannelOptionMapping,
    ChannelProduct,
    ChannelUploadSnapshot,
    MasterProduct,
    MasterProductOption,
)
from app.services.api_log_service import create_api_log
from app.services.smartstore.client import get_smartstore_client
from app.services.smartstore.mapper import build_product_payload
from app.services.smartstore_validation import create_upload_failure, validate_master_for_smartstore


def ensure_smartstore_channel(db: Session) -> Channel:
    channel = db.scalar(select(Channel).where(Channel.code == "smartstore"))
    if channel:
        return channel
    channel = Channel(name="Smartstore", code="smartstore", api_base_url="mock://smartstore")
    db.add(channel)
    db.flush()
    return channel


def build_payload_for_master(db: Session, master_product_id: int) -> dict:
    master = db.scalar(
        select(MasterProduct)
        .options(selectinload(MasterProduct.options))
        .where(MasterProduct.id == master_product_id)
    )
    if master is None:
        raise ValueError("master product not found")
    return build_product_payload(master)


def upload_master_product(db: Session, master_product_id: int) -> ChannelProduct:
    channel = ensure_smartstore_channel(db)
    master = db.scalar(
        select(MasterProduct)
        .options(selectinload(MasterProduct.options))
        .where(MasterProduct.id == master_product_id)
    )
    if master is None:
        raise ValueError("master product not found")

    validation_result = validate_master_for_smartstore(db, master_product_id)
    if not validation_result["valid"]:
        create_upload_failure(db, master_product_id, validation_result)
        create_api_log(
            db=db,
            service_name="mock_smartstore",
            endpoint="/products/validate",
            method="POST",
            request_json={"master_product_id": master_product_id},
            response_json=validation_result,
            status_code=422,
            success=False,
            error_message="Smartstore pre-validation failed",
        )
        db.commit()
        raise ValueError("smartstore validation failed")

    payload = build_product_payload(master)
    client = get_smartstore_client()
    response = client.upload_product(payload)

    channel_product = ChannelProduct(
        channel_id=channel.id,
        master_product_id=master.id,
        channel_product_id=response["channel_product_id"],
        channel_status="uploaded" if response.get("success") else "failed",
        raw_request_json=payload,
        raw_response_json=response,
        last_uploaded_at="2026-07-04T00:00:00",
    )
    db.add(channel_product)
    db.flush()

    options_by_code = {option.internal_option_code: option for option in master.options}
    for mapping in response.get("option_mappings", []):
        master_option: MasterProductOption | None = options_by_code.get(mapping["internal_option_code"])
        if master_option is None:
            continue
        db.add(
            ChannelOptionMapping(
                channel_product_id=channel_product.id,
                master_option_id=master_option.id,
                channel_option_id=mapping["channel_option_id"],
                channel_sku_code=mapping.get("channel_sku_code"),
                stock_quantity=master_option.stock_quantity,
                status=master_option.status,
            )
        )

    db.add(
        ChannelUploadSnapshot(
            channel_product_id=channel_product.id,
            snapshot_type="last_uploaded",
            product_name=master.cleaned_name or master.product_name,
            sale_price=master.sale_price,
            stock_quantity=sum(option.stock_quantity for option in master.options),
            status=master.status,
            payload_json=payload,
        )
    )
    master.status = "listed" if response.get("success") else "error"
    create_api_log(
        db=db,
        service_name="mock_smartstore",
        endpoint="/products",
        method="POST",
        request_json=payload,
        response_json=response,
        status_code=200 if response.get("success") else 500,
        success=bool(response.get("success")),
        error_message=None if response.get("success") else "Mock upload failed",
    )
    db.commit()
    db.refresh(channel_product)
    return channel_product
