from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List

from app.core.config import get_settings
from app.pipeline.ingest_manager import ChannelDirection


class DetectorModel(str, Enum):
    yolov8 = "yolov8"
    yolov11 = "yolov11"


class Device(str, Enum):
    cpu = "cpu"
    cuda = "cuda"


class TrackerType(str, Enum):
    bytetrack = "bytetrack"
    sort = "sort"


class OcrEngine(str, Enum):
    easyocr = "easyocr"
    paddleocr = "paddleocr"
    crnn = "crnn"


@dataclass
class DetectorSettings:
    model: DetectorModel = DetectorModel.yolov8
    device: Device = Device.cuda
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_detections: int = 10
    require_roi: bool = False


@dataclass
class TrackerSettings:
    tracker: TrackerType = TrackerType.bytetrack
    max_age: int = 30
    min_hits: int = 3
    match_iou_threshold: float = 0.5


@dataclass
class OcrSettings:
    engine: OcrEngine = OcrEngine.easyocr
    vote_frames: int = 3
    min_confidence: float = 0.6
    languages: List[str] = field(default_factory=lambda: ["en", "ru"])


@dataclass
class Detection:
    bbox: List[float]
    confidence: float


@dataclass
class Track:
    track_id: str
    bbox: List[float]
    direction: ChannelDirection
    confidence: float


@dataclass
class OcrCandidate:
    text: str
    confidence: float


@dataclass
class FrameRecognition:
    frame_id: str
    detections: List[Detection] = field(default_factory=list)
    tracks: List[Track] = field(default_factory=list)
    ocr: List[OcrCandidate] = field(default_factory=list)

    def as_dict(self) -> dict:
        def dict_factory(items: list[tuple[str, object]]) -> dict:
            return {key: (value.value if isinstance(value, Enum) else value) for key, value in items}

        return {
            "frame_id": self.frame_id,
            "detections": [asdict(det, dict_factory=dict_factory) for det in self.detections],
            "tracks": [asdict(track, dict_factory=dict_factory) for track in self.tracks],
            "ocr": [asdict(candidate, dict_factory=dict_factory) for candidate in self.ocr],
        }


class RecognitionPipeline:
    """Container for detector, tracker and OCR runtime settings.

    The actual ML models will be wired in future steps. For now, the pipeline
    exposes configuration and placeholder processing compatible with the
    roadmap. This keeps API contracts stable while models are integrated.
    """

    def __init__(
        self,
        detector_settings: DetectorSettings,
        tracker_settings: TrackerSettings,
        ocr_settings: OcrSettings,
    ) -> None:
        self.detector_settings = detector_settings
        self.tracker_settings = tracker_settings
        self.ocr_settings = ocr_settings

    def describe(self) -> dict:
        def dict_factory(items: list[tuple[str, object]]) -> dict:
            return {key: (value.value if isinstance(value, Enum) else value) for key, value in items}

        return {
            "detector": asdict(self.detector_settings, dict_factory=dict_factory),
            "tracker": asdict(self.tracker_settings, dict_factory=dict_factory),
            "ocr": asdict(self.ocr_settings, dict_factory=dict_factory),
        }

    def process_frame(self, frame_id: str, *, roi_applied: bool = False) -> FrameRecognition:
        detections: List[Detection] = []
        tracks: List[Track] = []
        ocr: List[OcrCandidate] = []

        if self.detector_settings.require_roi and not roi_applied:
            return FrameRecognition(frame_id=frame_id)

        # Placeholder: actual inference and tracking will be implemented later.
        return FrameRecognition(frame_id=frame_id, detections=detections, tracks=tracks, ocr=ocr)


_settings = get_settings()

recognition_pipeline = RecognitionPipeline(
    detector_settings=DetectorSettings(
        model=DetectorModel(_settings.detector_model),
        device=Device(_settings.detector_device),
        confidence_threshold=_settings.detector_confidence_threshold,
        iou_threshold=_settings.detector_iou_threshold,
        max_detections=_settings.detector_max_detections,
        require_roi=_settings.detector_require_roi,
    ),
    tracker_settings=TrackerSettings(
        tracker=TrackerType(_settings.tracker_type),
        max_age=_settings.tracker_max_age,
        min_hits=_settings.tracker_min_hits,
        match_iou_threshold=_settings.tracker_match_iou_threshold,
    ),
    ocr_settings=OcrSettings(
        engine=OcrEngine(_settings.ocr_engine),
        vote_frames=_settings.ocr_vote_frames,
        min_confidence=_settings.ocr_min_confidence,
        languages=_settings.ocr_languages,
    ),
)
