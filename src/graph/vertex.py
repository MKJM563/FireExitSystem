from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from src.graph.vertex_type import VertexType
from src.graph.accessibility_flags import AccessibilityFlags


@dataclass
class Location:
    x: float
    y: float
    floor: int


class Vertex:
    def __init__(self, id: int, x: float, y: float, floor: int, type: VertexType) -> None:
        self._id: int = id
        self._x: float = x
        self._y: float = y
        self._floor: int = floor
        self._type: VertexType = type
        self._device_ids: List[int] = []
        self._accessibility_flags: AccessibilityFlags = AccessibilityFlags(True, False, True)
        self._is_hazard: bool = False
        self._hazard_timestamp: Optional[datetime] = None
        self._hazard_confidence: float = 0.0

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> VertexType:
        return self._type

    @property
    def floor(self) -> int:
        return self._floor

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def is_hazard(self) -> bool:
        return self._is_hazard

    @property
    def hazard_confidence(self) -> float:
        return self._hazard_confidence

    @property
    def accessibility_flags(self) -> AccessibilityFlags:
        return self._accessibility_flags

    @accessibility_flags.setter
    def accessibility_flags(self, flags: AccessibilityFlags) -> None:
        self._accessibility_flags = flags

    def add_device(self, device_id: int) -> None:
        if device_id not in self._device_ids:
            self._device_ids.append(device_id)

    def remove_device(self, device_id: int) -> None:
        if device_id in self._device_ids:
            self._device_ids.remove(device_id)

    def mark_as_hazard(self, timestamp: datetime, confidence: float = 1.0) -> None:
        self._is_hazard = True
        self._hazard_timestamp = timestamp
        self._hazard_confidence = confidence

    def clear_hazard(self) -> None:
        self._is_hazard = False
        self._hazard_timestamp = None
        self._hazard_confidence = 0.0

    def get_location(self) -> Location:
        return Location(x=self._x, y=self._y, floor=self._floor)

    def is_accessible(self, requirements: AccessibilityFlags) -> bool:
        return self._accessibility_flags.matches(requirements)

    def get_device_ids(self) -> List[int]:
        return list(self._device_ids)

    def __repr__(self) -> str:
        return f"Vertex(id={self._id}, type={self._type}, floor={self._floor})"
