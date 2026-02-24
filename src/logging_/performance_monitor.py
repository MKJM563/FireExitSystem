from datetime import timedelta
from typing import Dict

from src.logging_.metric import Metric


class PerformanceMonitor:
    def __init__(self) -> None:
        self._metrics: Dict[str, Metric] = {}

    def _get_or_create(self, name: str) -> Metric:
        if name not in self._metrics:
            self._metrics[name] = Metric(name)
        return self._metrics[name]

    def record_calculation_time(self, duration: timedelta) -> None:
        self._get_or_create("calculation_time_ms").record(duration.total_seconds() * 1000)

    def record_message_processing_time(self, duration: timedelta) -> None:
        self._get_or_create("message_processing_time_ms").record(duration.total_seconds() * 1000)

    def record_cache_hit_rate(self, hits: int, misses: int) -> None:
        total = hits + misses
        rate = hits / total if total > 0 else 0.0
        self._get_or_create("cache_hit_rate").record(rate)
        self._get_or_create("cache_hits").record(float(hits))
        self._get_or_create("cache_misses").record(float(misses))

    def get_metrics(self) -> Dict[str, Metric]:
        return dict(self._metrics)

    def reset(self) -> None:
        self._metrics.clear()
