"""enhance master product review fields

Revision ID: 20260704_0005
Revises: 20260704_0004
Create Date: 2026-07-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260704_0005"
down_revision: str | None = "20260704_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("master_products")}
    add_if_missing(columns, "brand", sa.Column("brand", sa.String(length=100), nullable=True))
    add_if_missing(columns, "manufacturer", sa.Column("manufacturer", sa.String(length=100), nullable=True))
    add_if_missing(columns, "origin", sa.Column("origin", sa.String(length=100), nullable=True))
    add_if_missing(columns, "search_tags", sa.Column("search_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    add_if_missing(columns, "notice_info_json", sa.Column("notice_info_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    add_if_missing(
        columns,
        "validation_status",
        sa.Column("validation_status", sa.String(length=30), nullable=False, server_default="not_checked"),
    )
    add_if_missing(
        columns,
        "validation_issues_json",
        sa.Column("validation_issues_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.execute("UPDATE master_products SET validation_status = 'not_checked' WHERE validation_status IS NULL")
    op.alter_column("master_products", "validation_status", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("master_products")}
    for column_name in [
        "validation_issues_json",
        "validation_status",
        "notice_info_json",
        "search_tags",
        "origin",
        "manufacturer",
        "brand",
    ]:
        if column_name in columns:
            op.drop_column("master_products", column_name)


def add_if_missing(existing_columns: set[str], column_name: str, column: sa.Column) -> None:
    if column_name not in existing_columns:
        op.add_column("master_products", column)
        existing_columns.add(column_name)
