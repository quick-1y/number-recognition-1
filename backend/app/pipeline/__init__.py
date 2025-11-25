"""Pipeline components for the number recognition service."""

from .ingest_manager import ChannelConfig, ChannelDirection, DecoderPriority, IngestManager, IngestStatus, ingest_manager
from .postprocess import (
    CountryTemplate,
    PostprocessResult,
    PostprocessSettings,
    Postprocessor,
    postprocess_settings,
    postprocessor,
)
from .recognition import (
    Detection,
    DetectorModel,
    DetectorSettings,
    Device,
    FrameRecognition,
    OcrCandidate,
    OcrEngine,
    OcrSettings,
    RecognitionPipeline,
    Track,
    TrackerSettings,
    TrackerType,
    recognition_pipeline,
)

__all__ = [
    "IngestManager",
    "IngestStatus",
    "ChannelConfig",
    "ChannelDirection",
    "DecoderPriority",
    "ingest_manager",
    "CountryTemplate",
    "PostprocessSettings",
    "PostprocessResult",
    "Postprocessor",
    "postprocess_settings",
    "postprocessor",
    "Detection",
    "DetectorModel",
    "DetectorSettings",
    "Device",
    "FrameRecognition",
    "OcrCandidate",
    "OcrEngine",
    "OcrSettings",
    "RecognitionPipeline",
    "Track",
    "TrackerSettings",
    "TrackerType",
    "recognition_pipeline",
]
