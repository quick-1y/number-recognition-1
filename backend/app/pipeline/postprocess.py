from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from typing import List, Optional

from app.core.config import get_settings
from app.pipeline.recognition import OcrCandidate


@dataclass
class CountryTemplate:
    code: str
    pattern: str
    enabled: bool = True


@dataclass
class PostprocessSettings:
    vote_by_char: bool = True
    min_confidence: float = 0.55
    min_frames_for_event: int = 3
    anti_duplicate_seconds: int = 5
    country_templates: List[CountryTemplate] = field(default_factory=list)

    def describe(self) -> dict:
        return {
            "vote_by_char": self.vote_by_char,
            "min_confidence": self.min_confidence,
            "min_frames_for_event": self.min_frames_for_event,
            "anti_duplicate_seconds": self.anti_duplicate_seconds,
            "country_templates": [asdict(template) for template in self.country_templates],
        }


@dataclass
class PostprocessResult:
    plate: Optional[str]
    confidence: float
    country: Optional[str]
    is_duplicate: bool
    reason: Optional[str] = None

    def as_dict(self) -> dict:
        return asdict(self)


class Postprocessor:
    """Lightweight post-processing logic for OCR candidates.

    - Normalizes OCR strings and fixes common look-alike characters.
    - Performs per-character voting (optional) and validates against country templates.
    - Implements anti-duplicate suppression within a configurable time window.
    """

    _similar_chars_map = {
        "0": "O",
        "O": "0",
        "1": "I",
        "I": "1",
        "B": "8",
        "8": "B",
        "Z": "2",
        "2": "Z",
        "C": "С",  # Latin C to Cyrillic
        "С": "C",  # Cyrillic to Latin
    }

    def __init__(self, settings: PostprocessSettings) -> None:
        self.settings = settings
        self._country_regex = [
            (template.code.upper(), re.compile(template.pattern, re.IGNORECASE))
            for template in self.settings.country_templates
            if template.enabled
        ]
        self._recent: dict[str, float] = {}

    def normalize(self, text: str) -> str:
        normalized = text.strip().upper().replace(" ", "").replace("-", "")
        normalized = "".join(self._similar_chars_map.get(ch, ch) for ch in normalized)
        return normalized

    def _vote_by_char(self, candidates: list[OcrCandidate]) -> tuple[str, float]:
        if not candidates:
            return "", 0.0
        max_len = max(len(candidate.text) for candidate in candidates)
        voted_chars: list[str] = []
        total_conf = 0.0
        for idx in range(max_len):
            counter: dict[str, float] = {}
            for candidate in candidates:
                if idx >= len(candidate.text):
                    continue
                ch = candidate.text[idx].upper()
                counter[ch] = counter.get(ch, 0.0) + candidate.confidence
                total_conf += candidate.confidence / max_len
            if counter:
                voted_chars.append(max(counter, key=counter.get))
        text = "".join(voted_chars)
        return text, total_conf / max_len if voted_chars else 0.0

    def _best_candidate(self, candidates: list[OcrCandidate]) -> tuple[str, float]:
        best = max(candidates, key=lambda c: c.confidence)
        return best.text.upper(), best.confidence

    def _match_country(self, plate: str) -> Optional[str]:
        for code, pattern in self._country_regex:
            if pattern.match(plate):
                return code
        return None

    def _is_duplicate(self, plate: str, now: float) -> bool:
        last_seen = self._recent.get(plate)
        if last_seen is None:
            self._recent[plate] = now
            return False
        if now - last_seen <= self.settings.anti_duplicate_seconds:
            return True
        self._recent[plate] = now
        return False

    def process_candidates(
        self,
        candidates: list[OcrCandidate],
        *,
        frames_with_plate: int,
    ) -> PostprocessResult:
        eligible = [c for c in candidates if c.confidence >= self.settings.min_confidence]
        if frames_with_plate < self.settings.min_frames_for_event:
            return PostprocessResult(None, 0.0, None, False, reason="not_enough_frames")
        if not eligible:
            return PostprocessResult(None, 0.0, None, False, reason="low_confidence")

        if self.settings.vote_by_char:
            text, confidence = self._vote_by_char(eligible)
        else:
            text, confidence = self._best_candidate(eligible)

        normalized = self.normalize(text)
        country = self._match_country(normalized)
        now = time.time()
        duplicate = self._is_duplicate(normalized, now)

        return PostprocessResult(normalized, confidence, country, duplicate)


_default_country_patterns = {
    "ru": r"^[ABCEHKMOPTXУABCEHKMOPTXУ]{1}\d{3}[ABCEHKMOPTXУ]{2}\d{2,3}$",
    "by": r"^\d{4}[ABCEHKMOPTXУ]{2}-\d$",
    "kz": r"^[ABCEHKMOPTXУ]{3}\d{3}[ABCEHKMOPTXУ]{2}$",
    "ua": r"^[ABCEHIKMOPTX]{2}\d{4}[ABCEHIKMOPTX]{2}$",
    "eu": r"^[A-Z0-9]{6,8}$",
}

_settings = get_settings()

postprocess_settings = PostprocessSettings(
    vote_by_char=_settings.postprocess_vote_by_char,
    min_confidence=_settings.postprocess_min_confidence,
    min_frames_for_event=_settings.postprocess_min_frames_for_event,
    anti_duplicate_seconds=_settings.postprocess_anti_duplicate_seconds,
    country_templates=[
        CountryTemplate(code=code, pattern=_default_country_patterns[code], enabled=code in _settings.postprocess_country_templates)
        for code in _default_country_patterns
    ],
)

postprocessor = Postprocessor(postprocess_settings)
