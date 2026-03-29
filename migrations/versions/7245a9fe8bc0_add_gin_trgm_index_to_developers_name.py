"""add gin trgm index to developers name

Revision ID: 7245a9fe8bc0
Revises: 6222a70891aa
Create Date: 2026-03-29

"""

from collections.abc import Sequence

from alembic import op

revision: str = "7245a9fe8bc0"
down_revision: str | None = "6222a70891aa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_developers_name_trgm",
        "developers",
        ["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_developers_name_trgm", table_name="developers")
