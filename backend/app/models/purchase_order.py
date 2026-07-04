from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin


class PurchaseOrder(TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier_product_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    supplier_option_id: Mapped[str | None] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    receiver_name: Mapped[str | None] = mapped_column(String(100))
    receiver_phone: Mapped[str | None] = mapped_column(String(50))
    receiver_address: Mapped[str | None] = mapped_column(String(1000))
    delivery_message: Mapped[str | None] = mapped_column(String(1000))
    purchase_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    admin_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_request_json: Mapped[dict | None] = mapped_column(JSONB)
    raw_response_json: Mapped[dict | None] = mapped_column(JSONB)

    order_item = relationship("OrderItem", back_populates="purchase_order")
