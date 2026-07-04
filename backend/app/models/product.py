from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin


class SupplierProduct(TimestampMixin, Base):
    __tablename__ = "supplier_products"
    __table_args__ = (UniqueConstraint("supplier_id", "supplier_product_id", name="uq_supplier_product"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier_product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_description: Mapped[str | None] = mapped_column(Text)
    raw_category: Mapped[str | None] = mapped_column(String(300))
    brand: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    origin: Mapped[str | None] = mapped_column(String(100))
    supply_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shipping_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_sold_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_discontinued: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    main_image_url: Mapped[str | None] = mapped_column(String(1000))
    detail_image_urls: Mapped[list | None] = mapped_column(JSONB)
    certification_info: Mapped[dict | None] = mapped_column(JSONB)
    raw_payload_json: Mapped[dict | None] = mapped_column(JSONB)
    last_synced_at: Mapped[str | None] = mapped_column(String(50))

    supplier = relationship("Supplier", back_populates="products")
    options = relationship("SupplierProductOption", back_populates="supplier_product", cascade="all, delete-orphan")
    master_product = relationship("MasterProduct", back_populates="supplier_product", uselist=False)


class SupplierProductOption(TimestampMixin, Base):
    __tablename__ = "supplier_product_options"
    __table_args__ = (UniqueConstraint("supplier_product_id", "supplier_option_id", name="uq_supplier_product_option"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_product_id: Mapped[int] = mapped_column(ForeignKey("supplier_products.id"), nullable=False, index=True)
    supplier_option_id: Mapped[str] = mapped_column(String(100), nullable=False)
    option_name: Mapped[str | None] = mapped_column(String(200))
    option_value: Mapped[str | None] = mapped_column(String(300))
    option_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    supply_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_sold_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_discontinued: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_payload_json: Mapped[dict | None] = mapped_column(JSONB)

    supplier_product = relationship("SupplierProduct", back_populates="options")
    master_options = relationship("MasterProductOption", back_populates="supplier_option")


class MasterProduct(TimestampMixin, Base):
    __tablename__ = "master_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    internal_product_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    supplier_product_id: Mapped[int] = mapped_column(ForeignKey("supplier_products.id"), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(500))
    cleaned_name: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[str | None] = mapped_column(String(100))
    supply_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shipping_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sale_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    margin_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    expected_margin_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    main_image_url: Mapped[str | None] = mapped_column(String(1000))
    detail_image_urls: Mapped[list | None] = mapped_column(JSONB)
    certification_info: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    review_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    price_review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    supplier_product = relationship("SupplierProduct", back_populates="master_product")
    options = relationship("MasterProductOption", back_populates="master_product", cascade="all, delete-orphan")
    channel_products = relationship("ChannelProduct", back_populates="master_product")


class MasterProductOption(TimestampMixin, Base):
    __tablename__ = "master_product_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    master_product_id: Mapped[int] = mapped_column(ForeignKey("master_products.id"), nullable=False, index=True)
    internal_option_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    supplier_option_id: Mapped[int | None] = mapped_column(ForeignKey("supplier_product_options.id"))
    option_name: Mapped[str | None] = mapped_column(String(200))
    option_value: Mapped[str | None] = mapped_column(String(300))
    supply_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sale_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)

    master_product = relationship("MasterProduct", back_populates="options")
    supplier_option = relationship("SupplierProductOption", back_populates="master_options")
    channel_mappings = relationship("ChannelOptionMapping", back_populates="master_option")
