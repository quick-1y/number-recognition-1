"""Add channels table

Revision ID: 0002_add_channels
Revises: 0001_create_users
Create Date: 2024-05-23
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_channels"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    channel_direction = sa.Enum("up", "down", "any", name="channel_direction")
    channel_direction.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "channels",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=1024), nullable=False),
        sa.Column("protocol", sa.String(length=16), nullable=False, server_default="rtsp"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("target_fps", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("reconnect_seconds", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("decoder_priority", sa.String(length=64), nullable=False, server_default="nvdec,vaapi,cpu"),
        sa.Column("direction", channel_direction, nullable=False, server_default="any"),
        sa.Column("roi", sa.JSON(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("channels")
    sa.Enum(name="channel_direction").drop(op.get_bind(), checkfirst=True)
