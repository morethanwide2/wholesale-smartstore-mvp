from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin


class Channel(TimestampMixin, Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    api_base_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    products = relationship("ChannelProduct", back_populates="channel")
    orders = relationship("Order", back_populates="channel")


class ChannelProduct(TimestampMixin, Base):
    __tablename__ = "channel_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)
    master_product_id: Mapped[int] = mapped_column(ForeignKey("master_products.id"), nullable=False, index=True)
    channel_product_id: Mapped[str | None] = mapped_column(String(100), index=True)
    channel_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    last_uploaded_at: Mapped[str | None] = mapped_column(String(50))
    last_synced_at: Mapped[str | None] = mapped_column(String(50))
    raw_request_json: Mapped[dict | None] = mapped_column(JSONB)
    raw_response_json: Mapped[dict | None] = mapped_column(JSONB)

    channel = relationship("Channel", back_populates="products")
    master_product = relationship("MasterProduct", back_populates="channel_products")
    option_mappings = relationship("ChannelOptionMapping", back_populates="channel_product")


class ChannelProductProfile(TimestampMixin, Base):
    __tablename__ = "channel_product_profiles"
    __table_args__ = (UniqueConstraint("channel_id", "master_product_id", name="uq_channel_product_profile"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)
    master_product_id: Mapped[int] = mapped_column(ForeignKey("master_products.id"), nullable=False, index=True)
    channel_product_name: Mapped[str | None] = mapped_column(String(500))
    channel_category_id: Mapped[str | None] = mapped_column(String(100))
    channel_sale_price: Mapped[int | None] = mapped_column(Integer)
    channel_shipping_fee: Mapped[int | None] = mapped_column(Integer)
    channel_attributes_json: Mapped[dict | None] = mapped_column(JSONB)
    channel_status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    use_master_name: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    use_master_price: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    use_master_images: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    upload_validation_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_checked", index=True)
    last_validation_json: Mapped[dict | None] = mapped_column(JSONB)

    channel = relationship("Channel")
    master_product = relationship("MasterProduct")


class ChannelUploadSnapshot(Base):
    __tablename__ = "channel_upload_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_product_id: Mapped[int] = mapped_column(ForeignKey("channel_products.id"), nullable=False, index=True)
    snapshot_type: Mapped[str] = mapped_column(String(30), nullable=False, default="last_uploaded", index=True)
    product_name: Mapped[str | None] = mapped_column(String(500))
    sale_price: Mapped[int | None] = mapped_column(Integer)
    stock_quantity: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(30))
    payload_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    channel_product = relationship("ChannelProduct")


class ChannelOptionMapping(TimestampMixin, Base):
    __tablename__ = "channel_option_mapping"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_product_id: Mapped[int] = mapped_column(ForeignKey("channel_products.id"), nullable=False, index=True)
    master_option_id: Mapped[int] = mapped_column(ForeignKey("master_product_options.id"), nullable=False, index=True)
    channel_option_id: Mapped[str | None] = mapped_column(String(100), index=True)
    channel_sku_code: Mapped[str | None] = mapped_column(String(100))
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    channel_product = relationship("ChannelProduct", back_populates="option_mappings")
    master_option = relationship("MasterProductOption", back_populates="channel_mappings")
