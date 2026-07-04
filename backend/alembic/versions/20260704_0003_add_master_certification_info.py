"""add master certification info

Revision ID: 20260704_0003
Revises: 20260704_0002
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260704_0003"
down_revision: str | None = "20260704_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("master_products")}
    if "certification_info" not in columns:
        op.add_column(
            "master_products",
            sa.Column("certification_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("master_products")}
    if "certification_info" in columns:
        op.drop_column("master_products", "certification_info")
