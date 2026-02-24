from __future__ import annotations
from collections import deque
from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.graph.building_graph import BuildingGraph


class Hazard:
    def __init__(self, device_id: int, vertex_id: int, confidence: float) -> None:
        self._device_id: int = device_id
        self._vertex_id: int = vertex_id
        self._detection_time: datetime = datetime.now()
        self._confidence: float = max(0.0, min(1.0, confidence))
        self._current_radius: int = 0
        self._max_radius: int = 5
        self._is_active: bool = True

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def vertex_id(self) -> int:
        return self._vertex_id

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def current_radius(self) -> int:
        return self._current_radius

    @property
    def is_active(self) -> bool:
        return self._is_active

    def spread_radius(self) -> None:
        if self._is_active and self._current_radius < self._max_radius:
            self._current_radius += 1

    def deactivate(self) -> None:
        self._is_active = False

    def get_affected_vertices(self, graph: "BuildingGraph") -> List[int]:
        """BFS from vertexId up to currentRadius hops."""
        visited: set = {self._vertex_id}
        frontier: deque = deque([(self._vertex_id, 0)])
        result: List[int] = []

        while frontier:
            current_id, depth = frontier.popleft()
            result.append(current_id)
            if depth < self._current_radius:
                for edge in graph.get_neighbors(current_id):
                    if edge.dest_id not in visited:
                        visited.add(edge.dest_id)
                        frontier.append((edge.dest_id, depth + 1))

        return result

    def get_age(self) -> timedelta:
        return datetime.now() - self._detection_time

    def __repr__(self) -> str:
        return (
            f"Hazard(device={self._device_id}, vertex={self._vertex_id}, "
            f"confidence={self._confidence:.2f}, radius={self._current_radius})"
        )
