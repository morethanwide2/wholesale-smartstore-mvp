from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import TimestampMixin


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    master_product_id: Mapped[int] = mapped_column(ForeignKey("master_products.id"), nullable=False, index=True)
    master_option_id: Mapped[int | None] = mapped_column(ForeignKey("master_product_options.id"))
    previous_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    change_reason: Mapped[str | None] = mapped_column(String(300))
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="supplier")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PriceLog(Base):
    __tablename__ = "price_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    master_product_id: Mapped[int] = mapped_column(ForeignKey("master_products.id"), nullable=False, index=True)
    master_option_id: Mapped[int | None] = mapped_column(ForeignKey("master_product_options.id"))
    previous_supply_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_supply_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    previous_sale_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_sale_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    change_reason: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ShipmentLog(TimestampMixin, Base):
    __tablename__ = "shipment_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    purchase_order_id: Mapped[int | None] = mapped_column(ForeignKey("purchase_orders.id"))
    courier_name: Mapped[str | None] = mapped_column(String(100))
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    shipped_at: Mapped[str | None] = mapped_column(String(50))
    sent_to_channel: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ApiLog(Base):
    __tablename__ = "api_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    request_json: Mapped[dict | None] = mapped_column(JSONB)
    response_json: Mapped[dict | None] = mapped_column(JSONB)
    status_code: Mapped[int | None] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    error_message: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ErrorQueue(TimestampMixin, Base):
    __tablename__ = "error_queue"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    related_entity_type: Mapped[str | None] = mapped_column(String(100))
    related_entity_id: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str] = mapped_column(String(2000), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    next_retry_at: Mapped[str | None] = mapped_column(String(50))


class ApiRateLimitSetting(TimestampMixin, Base):
    __tablename__ = "api_rate_limit_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    max_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    min_interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ApiJob(TimestampMixin, Base):
    __tablename__ = "api_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    related_entity_type: Mapped[str | None] = mapped_column(String(100))
    related_entity_id: Mapped[int | None] = mapped_column(Integer, index=True)
    dedupe_key: Mapped[str] = mapped_column(String(300), nullable=False, unique=True, index=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    last_error_message: Mapped[str | None] = mapped_column(String(2000))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
