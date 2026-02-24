from __future__ import annotations
import logging
import logging.handlers
from datetime import timedelta
from typing import Optional, TYPE_CHECKING

from src.logging_.log_level import LogLevel

if TYPE_CHECKING:
    from src.route.route import Route
    from src.hazard.hazard import Hazard
    from src.thread.recalculation_trigger import RecalculationTrigger

_LEVEL_MAP = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
}


class RouteLogger:
    def __init__(self, path: str, level: LogLevel) -> None:
        self._log_file_path: str = path
        self._log_level: LogLevel = level
        self._logger: logging.Logger = logging.getLogger("RouteLogger")
        self._logger.setLevel(_LEVEL_MAP[level])

        if not self._logger.handlers:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
            file_handler = logging.FileHandler(path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

    def log_route_calculation(
        self,
        route: "Route",
        trigger: "RecalculationTrigger",
        compute_time: timedelta,
    ) -> None:
        self._logger.info(
            "Route calculated | path_len=%d dist=%.2f trigger=%s compute_ms=%.1f",
            len(route.vertex_path),
            route.total_distance,
            trigger.trigger_type.value,
            compute_time.total_seconds() * 1000,
        )

    def log_hazard_detection(self, hazard: "Hazard") -> None:
        self._logger.warning(
            "Hazard detected | device=%d vertex=%d confidence=%.2f",
            hazard.device_id,
            hazard.vertex_id,
            hazard.confidence,
        )

    def log_device_failure(self, device_id: int, vertex_id: int) -> None:
        self._logger.error(
            "Device failure | device=%d vertex=%d",
            device_id,
            vertex_id,
        )

    def log_recalculation_complete(self, route_count: int, compute_time: timedelta) -> None:
        self._logger.info(
            "Recalculation complete | routes=%d compute_ms=%.1f",
            route_count,
            compute_time.total_seconds() * 1000,
        )

    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        if exception:
            self._logger.error("%s | exception=%s", message, str(exception))
        else:
            self._logger.error("%s", message)

    def close(self) -> None:
        for handler in self._logger.handlers[:]:
            handler.close()
            self._logger.removeHandler(handler)
