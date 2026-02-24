from __future__ import annotations
import math
from datetime import datetime
from typing import List, Optional

from src.route.direction import Direction
from src.route.urgency_level import UrgencyLevel


class Route:
    def __init__(self, path: List[int], distance: float) -> None:
        self._vertex_path: List[int] = path
        self._total_distance: float = distance
        self._confidence_score: float = 1.0
        self._calculation_time: datetime = datetime.now()
        self._urgency: UrgencyLevel = UrgencyLevel.NORMAL

    @property
    def vertex_path(self) -> List[int]:
        return list(self._vertex_path)

    @property
    def total_distance(self) -> float:
        return self._total_distance

    @property
    def urgency(self) -> UrgencyLevel:
        return self._urgency

    @urgency.setter
    def urgency(self, level: UrgencyLevel) -> None:
        self._urgency = level

    def get_next_vertex(self, current_vertex: int) -> Optional[int]:
        """Return the vertex after current_vertex in the path, or None if at end."""
        try:
            idx = self._vertex_path.index(current_vertex)
            if idx + 1 < len(self._vertex_path):
                return self._vertex_path[idx + 1]
        except ValueError:
            pass
        return None

    def get_direction(self, current_vertex: int, sign_orientation: float) -> Direction:
        """Return a compass Direction based on the sign's orientation angle (degrees)."""
        # sign_orientation: 0 = North, 90 = East, etc.
        # Map angle to 8 compass directions relative to sign orientation
        angle = sign_orientation % 360
        sectors = [
            (22.5, Direction.NORTH),
            (67.5, Direction.NORTHEAST),
            (112.5, Direction.EAST),
            (157.5, Direction.SOUTHEAST),
            (202.5, Direction.SOUTH),
            (247.5, Direction.SOUTHWEST),
            (292.5, Direction.WEST),
            (337.5, Direction.NORTHWEST),
            (360.0, Direction.NORTH),
        ]
        for threshold, direction in sectors:
            if angle < threshold:
                return direction
        return Direction.FORWARD

    def get_distance_to_next(self, current_vertex: int) -> float:
        """Approximate distance to next vertex (returns total / path length as rough estimate)."""
        if len(self._vertex_path) <= 1:
            return 0.0
        return self._total_distance / max(1, len(self._vertex_path) - 1)

    def is_valid(self) -> bool:
        return len(self._vertex_path) >= 2 and self._total_distance >= 0

    def get_confidence_score(self) -> float:
        return self._confidence_score

    def set_confidence_score(self, score: float) -> None:
        self._confidence_score = max(0.0, min(1.0, score))

    def __repr__(self) -> str:
        return (
            f"Route(path={self._vertex_path}, distance={self._total_distance:.2f}, "
            f"confidence={self._confidence_score:.2f})"
        )
