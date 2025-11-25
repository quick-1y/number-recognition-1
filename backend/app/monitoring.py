from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings


@dataclass
class HistogramBucket:
    count: int = 0
    total: float = 0.0


class MetricsRegistry:
    def __init__(self, namespace: str, enabled: bool = True):
        self.namespace = namespace
        self.enabled = enabled
        self.counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self.gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
        self.histograms: dict[tuple[str, tuple[tuple[str, str], ...]], HistogramBucket] = defaultdict(HistogramBucket)

    @staticmethod
    def _label_key(labels: dict[str, str] | None) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(labels.items())) if labels else tuple()

    def inc(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        if not self.enabled:
            return
        key = (name, self._label_key(labels))
        self.counters[key] += value

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        if not self.enabled:
            return
        key = (name, self._label_key(labels))
        self.gauges[key] = value

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        if not self.enabled:
            return
        key = (name, self._label_key(labels))
        bucket = self.histograms[key]
        bucket.count += 1
        bucket.total += value

    def describe(self) -> dict[str, Any]:
        if not self.enabled:
            return {"enabled": False}
        return {
            "enabled": True,
            "namespace": self.namespace,
            "counters": {f"{k[0]}:{k[1]}": v for k, v in self.counters.items()},
            "gauges": {f"{k[0]}:{k[1]}": v for k, v in self.gauges.items()},
            "histograms": {
                f"{k[0]}:{k[1]}": {"count": bucket.count, "avg": bucket.total / bucket.count if bucket.count else 0.0}
                for k, bucket in self.histograms.items()
            },
        }

    def export_prometheus(self) -> str:
        if not self.enabled:
            return "# metrics disabled\n"
        lines: list[str] = []
        for (name, labels), value in self.counters.items():
            label_str = self._format_labels(labels)
            lines.append(f"{self.namespace}_{name}_total{label_str} {value}")
        for (name, labels), value in self.gauges.items():
            label_str = self._format_labels(labels)
            lines.append(f"{self.namespace}_{name}{label_str} {value}")
        for (name, labels), bucket in self.histograms.items():
            label_str = self._format_labels(labels)
            lines.append(f"{self.namespace}_{name}_count{label_str} {bucket.count}")
            avg = bucket.total / bucket.count if bucket.count else 0.0
            lines.append(f"{self.namespace}_{name}_avg{label_str} {avg}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _format_labels(labels: tuple[tuple[str, str], ...]) -> str:
        if not labels:
            return ""
        rendered = ",".join([f"{k}=\"{v}\"" for k, v in labels])
        return f"{{{rendered}}}"


def build_metrics_registry() -> MetricsRegistry:
    settings = get_settings()
    return MetricsRegistry(namespace=settings.metrics_namespace, enabled=settings.metrics_enabled)


def base_operational_snapshot() -> dict[str, Any]:
    return {
        "live": True,
        "ready": True,
    }


metrics_registry = build_metrics_registry()
