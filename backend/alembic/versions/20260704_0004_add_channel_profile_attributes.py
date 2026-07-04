"""add channel profile attributes

Revision ID: 20260704_0004
Revises: 20260704_0003
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260704_0004"
down_revision: str | None = "20260704_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("channel_product_profiles")}
    if "channel_attributes_json" not in columns:
        op.add_column(
            "channel_product_profiles",
            sa.Column("channel_attributes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("channel_product_profiles")}
    if "channel_attributes_json" in columns:
        op.drop_column("channel_product_profiles", "channel_attributes_json")
