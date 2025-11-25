import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    operator = "operator"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.operator)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ChannelDirection(str, enum.Enum):
    up = "up"
    down = "down"
    any = "any"


class Channel(Base):
    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    source = Column(String(1024), nullable=False)
    protocol = Column(String(16), nullable=False, default="rtsp")
    is_active = Column(Boolean, nullable=False, default=True)
    target_fps = Column(Integer, nullable=False, default=12)
    reconnect_seconds = Column(Integer, nullable=False, default=3)
    decoder_priority = Column(String(64), nullable=False, default="nvdec,vaapi,cpu")
    direction = Column(Enum(ChannelDirection, name="channel_direction"), nullable=False, default=ChannelDirection.any)
    roi = Column(JSON, nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
