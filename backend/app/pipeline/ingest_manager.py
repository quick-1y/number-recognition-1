from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class DecoderPriority(str, Enum):
    nvdec = "nvdec"
    vaapi = "vaapi"
    cpu = "cpu"


class ChannelDirection(str, Enum):
    up = "up"
    down = "down"
    any = "any"


@dataclass
class ChannelConfig:
    channel_id: str
    name: str
    source: str
    protocol: str = "rtsp"
    target_fps: int = 12
    reconnect_seconds: int = 3
    decoder_priority: List[DecoderPriority] = field(
        default_factory=lambda: [DecoderPriority.nvdec, DecoderPriority.vaapi, DecoderPriority.cpu]
    )
    direction: ChannelDirection = ChannelDirection.any
    roi: Optional[dict] = None
    description: Optional[str] = None


@dataclass
class IngestStatus:
    channel_id: str
    name: str
    state: str
    target_fps: int
    reconnect_seconds: int
    decoder_priority: List[str]
    last_connected_at: Optional[datetime] = None
    last_error: Optional[str] = None
    restart_count: int = 0

    def as_dict(self) -> dict:
        payload = asdict(self)
        if self.last_connected_at:
            payload["last_connected_at"] = self.last_connected_at.isoformat()
        return payload


class IngestManager:
    """Tracks ingest channel configurations and runtime state.

    The actual capture/decoder threads are intentionally left to later steps; this manager
    centralizes configuration, reconnection policy and monitoring endpoints.
    """

    def __init__(self, default_target_fps: int = 12, default_reconnect_seconds: int = 3):
        self._channels: Dict[str, IngestStatus] = {}
        self.default_target_fps = default_target_fps
        self.default_reconnect_seconds = default_reconnect_seconds

    def register_channel(self, config: ChannelConfig) -> IngestStatus:
        status = IngestStatus(
            channel_id=config.channel_id,
            name=config.name,
            state="configured",
            target_fps=config.target_fps or self.default_target_fps,
            reconnect_seconds=config.reconnect_seconds or self.default_reconnect_seconds,
            decoder_priority=[p.value for p in config.decoder_priority],
        )
        self._channels[config.channel_id] = status
        return status

    def remove_channel(self, channel_id: str) -> None:
        self._channels.pop(channel_id, None)

    def snapshot(self) -> List[dict]:
        return [status.as_dict() for status in self._channels.values()]

    def mark_connected(self, channel_id: str) -> None:
        status = self._channels.get(channel_id)
        if not status:
            return
        status.state = "streaming"
        status.last_connected_at = datetime.utcnow()
        status.last_error = None

    def mark_error(self, channel_id: str, error: str) -> None:
        status = self._channels.get(channel_id)
        if not status:
            return
        status.state = "reconnecting"
        status.last_error = error
        status.restart_count += 1


# Singleton manager for API exposure; actual workers will be attached in later steps.
ingest_manager = IngestManager()
