from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from src.graph.edge_status import EdgeStatus
from src.graph.accessibility_flags import AccessibilityFlags

if TYPE_CHECKING:
    from src.route.weight_factors import WeightFactors


class Edge:
    def __init__(self, source_id: int, dest_id: int, distance: float) -> None:
        self._source_id: int = source_id
        self._dest_id: int = dest_id
        self._base_distance: float = distance
        self._safety_score: float = 100.0
        self._congestion_factor: float = 1.0
        self._accessibility_flags: AccessibilityFlags = AccessibilityFlags(True, False, True)
        self._status: EdgeStatus = EdgeStatus.OPERATIONAL
        self._last_update_time: datetime = datetime.now()

    @property
    def source_id(self) -> int:
        return self._source_id

    @property
    def dest_id(self) -> int:
        return self._dest_id

    @property
    def base_distance(self) -> float:
        return self._base_distance

    @property
    def safety_score(self) -> float:
        return self._safety_score

    @property
    def congestion_factor(self) -> float:
        return self._congestion_factor

    @property
    def status(self) -> EdgeStatus:
        return self._status

    @property
    def accessibility_flags(self) -> AccessibilityFlags:
        return self._accessibility_flags

    @accessibility_flags.setter
    def accessibility_flags(self, flags: AccessibilityFlags) -> None:
        self._accessibility_flags = flags

    def update_safety_score(self, score: float) -> None:
        self._safety_score = max(0.0, min(100.0, score))
        self._last_update_time = datetime.now()

    def update_congestion(self, factor: float) -> None:
        self._congestion_factor = max(0.0, factor)
        self._last_update_time = datetime.now()

    def set_status(self, status: EdgeStatus) -> None:
        self._status = status
        self._last_update_time = datetime.now()

    def calculate_composite_weight(self, weights: "WeightFactors") -> float:
        """weight = distanceWeight * distance + safetyWeight * (100 - safetyScore) + congestionWeight * congestionFactor"""
        return (
            weights.distance_weight * self._base_distance
            + weights.safety_weight * (100.0 - self._safety_score)
            + weights.congestion_weight * self._congestion_factor
        )

    def is_passable(self) -> bool:
        return self._status not in (EdgeStatus.BLOCKED, EdgeStatus.IMPASSABLE)

    def is_accessible(self, requirements: AccessibilityFlags) -> bool:
        return self._accessibility_flags.matches(requirements)

    def __repr__(self) -> str:
        return f"Edge({self._source_id} -> {self._dest_id}, dist={self._base_distance}, status={self._status})"
