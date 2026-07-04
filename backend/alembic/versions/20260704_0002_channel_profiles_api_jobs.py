"""add channel profiles and api jobs

Revision ID: 20260704_0002
Revises: 20260704_0001
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260704_0002"
down_revision: str | None = "20260704_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("channel_product_profiles"):
        op.create_table(
            "channel_product_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("master_product_id", sa.Integer(), nullable=False),
        sa.Column("channel_product_name", sa.String(length=500), nullable=True),
        sa.Column("channel_category_id", sa.String(length=100), nullable=True),
        sa.Column("channel_sale_price", sa.Integer(), nullable=True),
        sa.Column("channel_shipping_fee", sa.Integer(), nullable=True),
        sa.Column("channel_status", sa.String(length=30), nullable=False),
        sa.Column("use_master_name", sa.Boolean(), nullable=False),
        sa.Column("use_master_price", sa.Boolean(), nullable=False),
        sa.Column("use_master_images", sa.Boolean(), nullable=False),
        sa.Column("upload_validation_status", sa.String(length=30), nullable=False),
        sa.Column("last_validation_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"]),
        sa.ForeignKeyConstraint(["master_product_id"], ["master_products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel_id", "master_product_id", name="uq_channel_product_profile"),
        )
        op.create_index(
            op.f("ix_channel_product_profiles_channel_id"),
            "channel_product_profiles",
            ["channel_id"],
        )
        op.create_index(
            op.f("ix_channel_product_profiles_master_product_id"),
            "channel_product_profiles",
            ["master_product_id"],
        )
        op.create_index(
            op.f("ix_channel_product_profiles_channel_status"),
            "channel_product_profiles",
            ["channel_status"],
        )
        op.create_index(
            op.f("ix_channel_product_profiles_upload_validation_status"),
            "channel_product_profiles",
            ["upload_validation_status"],
        )

    if not inspector.has_table("channel_upload_snapshots"):
        op.create_table(
            "channel_upload_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel_product_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_type", sa.String(length=30), nullable=False),
        sa.Column("product_name", sa.String(length=500), nullable=True),
        sa.Column("sale_price", sa.Integer(), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["channel_product_id"], ["channel_products.id"]),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_channel_upload_snapshots_channel_product_id"),
            "channel_upload_snapshots",
            ["channel_product_id"],
        )
        op.create_index(
            op.f("ix_channel_upload_snapshots_snapshot_type"),
            "channel_upload_snapshots",
            ["snapshot_type"],
        )

    if not inspector.has_table("api_rate_limit_settings"):
        op.create_table(
            "api_rate_limit_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_name", sa.String(length=100), nullable=False),
        sa.Column("max_per_minute", sa.Integer(), nullable=False),
        sa.Column("min_interval_seconds", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_api_rate_limit_settings_service_name"),
            "api_rate_limit_settings",
            ["service_name"],
            unique=True,
        )

    if not inspector.has_table("api_jobs"):
        op.create_table(
            "api_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_name", sa.String(length=100), nullable=False),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("related_entity_type", sa.String(length=100), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("dedupe_key", sa.String(length=300), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("max_attempt_count", sa.Integer(), nullable=False),
        sa.Column("last_error_message", sa.String(length=2000), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_api_jobs_service_name"), "api_jobs", ["service_name"])
        op.create_index(op.f("ix_api_jobs_job_type"), "api_jobs", ["job_type"])
        op.create_index(op.f("ix_api_jobs_related_entity_id"), "api_jobs", ["related_entity_id"])
        op.create_index(op.f("ix_api_jobs_dedupe_key"), "api_jobs", ["dedupe_key"], unique=True)
        op.create_index(op.f("ix_api_jobs_status"), "api_jobs", ["status"])
        op.create_index(op.f("ix_api_jobs_scheduled_at"), "api_jobs", ["scheduled_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_api_jobs_scheduled_at"), table_name="api_jobs")
    op.drop_index(op.f("ix_api_jobs_status"), table_name="api_jobs")
    op.drop_index(op.f("ix_api_jobs_dedupe_key"), table_name="api_jobs")
    op.drop_index(op.f("ix_api_jobs_related_entity_id"), table_name="api_jobs")
    op.drop_index(op.f("ix_api_jobs_job_type"), table_name="api_jobs")
    op.drop_index(op.f("ix_api_jobs_service_name"), table_name="api_jobs")
    op.drop_table("api_jobs")

    op.drop_index(op.f("ix_api_rate_limit_settings_service_name"), table_name="api_rate_limit_settings")
    op.drop_table("api_rate_limit_settings")

    op.drop_index(op.f("ix_channel_upload_snapshots_snapshot_type"), table_name="channel_upload_snapshots")
    op.drop_index(op.f("ix_channel_upload_snapshots_channel_product_id"), table_name="channel_upload_snapshots")
    op.drop_table("channel_upload_snapshots")

    op.drop_index(
        op.f("ix_channel_product_profiles_upload_validation_status"),
        table_name="channel_product_profiles",
    )
    op.drop_index(op.f("ix_channel_product_profiles_channel_status"), table_name="channel_product_profiles")
    op.drop_index(op.f("ix_channel_product_profiles_master_product_id"), table_name="channel_product_profiles")
    op.drop_index(op.f("ix_channel_product_profiles_channel_id"), table_name="channel_product_profiles")
    op.drop_table("channel_product_profiles")
