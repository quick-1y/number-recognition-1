"""add plate lists and items

Revision ID: 0003_add_plate_lists
Revises: 0002_add_channels
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0003_add_plate_lists"
down_revision = "0002_add_channels"
branch_labels = None
depends_on = None


def upgrade() -> None:
    plate_list_type = postgresql.ENUM("white", "black", "info", name="plate_list_type")
    plate_list_type.create(op.get_bind())

    op.create_table(
        "plate_lists",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.Enum("white", "black", "info", name="plate_list_type"), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("ttl_seconds", sa.Integer(), nullable=True),
        sa.Column("schedule", sa.JSON(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "plate_list_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plate_list_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pattern", sa.String(length=64), nullable=False),
        sa.Column("comment", sa.String(length=255), nullable=True),
        sa.Column("ttl_seconds", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["plate_list_id"], ["plate_lists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_plate_list_items_plate_list_id", "plate_list_items", ["plate_list_id"])


def downgrade() -> None:
    op.drop_index("ix_plate_list_items_plate_list_id", table_name="plate_list_items")
    op.drop_table("plate_list_items")
    op.drop_table("plate_lists")

    plate_list_type = postgresql.ENUM("white", "black", "info", name="plate_list_type")
    plate_list_type.drop(op.get_bind())
