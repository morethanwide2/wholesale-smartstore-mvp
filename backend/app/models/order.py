from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)
    channel_order_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    order_status: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False)
    ordered_at: Mapped[str] = mapped_column(String(50), nullable=False)
    buyer_name: Mapped[str | None] = mapped_column(String(100))
    receiver_name: Mapped[str | None] = mapped_column(String(100))
    receiver_phone: Mapped[str | None] = mapped_column(String(50))
    receiver_address: Mapped[str | None] = mapped_column(String(1000))
    delivery_message: Mapped[str | None] = mapped_column(String(1000))
    raw_payload_json: Mapped[dict | None] = mapped_column(JSONB)

    channel = relationship("Channel", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(TimestampMixin, Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    channel_product_id: Mapped[str | None] = mapped_column(String(100), index=True)
    channel_option_id: Mapped[str | None] = mapped_column(String(100), index=True)
    master_product_id: Mapped[int | None] = mapped_column(ForeignKey("master_products.id"))
    master_option_id: Mapped[int | None] = mapped_column(ForeignKey("master_product_options.id"))
    product_name: Mapped[str | None] = mapped_column(String(500))
    option_name: Mapped[str | None] = mapped_column(String(300))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    paid_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mapping_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unmatched", index=True)

    order = relationship("Order", back_populates="items")
    purchase_order = relationship("PurchaseOrder", back_populates="order_item", uselist=False)
