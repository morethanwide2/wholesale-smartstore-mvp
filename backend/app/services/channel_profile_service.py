from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Channel, ChannelProductProfile, MasterProduct
from app.services.smartstore_upload_service import ensure_smartstore_channel


def ensure_channel_profile(db: Session, channel_code: str, master_product_id: int) -> ChannelProductProfile:
    channel = _get_channel(db, channel_code)
    master = db.get(MasterProduct, master_product_id)
    if master is None:
        raise ValueError("master product not found")

    profile = db.scalar(
        select(ChannelProductProfile).where(
            ChannelProductProfile.channel_id == channel.id,
            ChannelProductProfile.master_product_id == master.id,
        )
    )
    if profile:
        return profile

    profile = ChannelProductProfile(
        channel_id=channel.id,
        master_product_id=master.id,
        channel_product_name=master.cleaned_name or master.product_name,
        channel_category_id=master.category_id,
        channel_sale_price=master.sale_price,
        channel_shipping_fee=master.shipping_fee,
        channel_attributes_json={},
        channel_status="draft",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_channel_profiles(db: Session, channel_code: str | None = None) -> list[ChannelProductProfile]:
    query = select(ChannelProductProfile).order_by(ChannelProductProfile.id.desc())
    if channel_code:
        channel = db.scalar(select(Channel).where(Channel.code == channel_code))
        if channel is None:
            return []
        query = query.where(ChannelProductProfile.channel_id == channel.id)
    return list(db.scalars(query).all())


def save_validation_result(db: Session, channel_code: str, master_product_id: int, validation_result: dict) -> None:
    profile = ensure_channel_profile(db, channel_code, master_product_id)
    profile.upload_validation_status = "passed" if validation_result.get("valid") else "failed"
    profile.last_validation_json = validation_result
    db.commit()


def _get_channel(db: Session, channel_code: str) -> Channel:
    if channel_code == "smartstore":
        return ensure_smartstore_channel(db)
    channel = db.scalar(select(Channel).where(Channel.code == channel_code))
    if channel:
        return channel
    channel = Channel(name=channel_code, code=channel_code, api_base_url=None)
    db.add(channel)
    db.flush()
    return channel
