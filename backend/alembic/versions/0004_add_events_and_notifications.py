"""Add recognition events, webhooks and alarm relays

Revision ID: 0004_add_events_and_notifications
Revises: 0003_add_plate_lists
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0004_add_events_and_notifications"
down_revision = "0003_add_plate_lists"
branch_labels = None
depends_on = None


def upgrade() -> None:
    relay_mode = postgresql.ENUM(
        "toggle", "close_open", "open_close", "hold_close", "hold_open", name="relay_mode"
    )
    relay_mode.create(op.get_bind())

    op.create_table(
        "alarm_relays",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("mode", sa.Enum("toggle", "close_open", "open_close", "hold_close", "hold_open", name="relay_mode"), nullable=False),
        sa.Column("delay_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("debounce_ms", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "recognitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("track_id", sa.String(length=64), nullable=True),
        sa.Column("plate", sa.String(length=32), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("country_pattern", sa.String(length=16), nullable=True),
        sa.Column("bbox", sa.JSON(), nullable=True),
        sa.Column("direction", sa.Enum("up", "down", "any", name="channel_direction"), nullable=True),
        sa.Column("image_url", sa.String(length=1024), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("best_frame_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("secret", sa.String(length=255), nullable=True),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "webhook_deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_code", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["subscription_id"], ["webhook_subscriptions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["event_id"], ["recognitions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_alarm_relays_channel_id", "alarm_relays", ["channel_id"])
    op.create_index("ix_recognitions_channel_id", "recognitions", ["channel_id"])
    op.create_index("ix_webhook_deliveries_subscription_id", "webhook_deliveries", ["subscription_id"])


def downgrade() -> None:
    op.drop_index("ix_webhook_deliveries_subscription_id", table_name="webhook_deliveries")
    op.drop_index("ix_recognitions_channel_id", table_name="recognitions")
    op.drop_index("ix_alarm_relays_channel_id", table_name="alarm_relays")

    op.drop_table("webhook_deliveries")
    op.drop_table("webhook_subscriptions")
    op.drop_table("recognitions")
    op.drop_table("alarm_relays")

    relay_mode = postgresql.ENUM(
        "toggle", "close_open", "open_close", "hold_close", "hold_open", name="relay_mode"
    )
    relay_mode.drop(op.get_bind())
