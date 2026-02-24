import json
from datetime import datetime

from src.messaging.message import Message
from src.messaging.message_type import MessageType
from src.route.direction import Direction
from src.route.urgency_level import UrgencyLevel


class RouteUpdateMessage(Message):
    def __init__(self, sign_id: int, direction: Direction, distance: float) -> None:
        super().__init__(MessageType.ROUTE_UPDATE)
        self._exit_sign_id: int = sign_id
        self._direction: Direction = direction
        self._distance_to_next: float = distance
        self._confidence_score: float = 1.0
        self._urgency: UrgencyLevel = UrgencyLevel.NORMAL

    @property
    def exit_sign_id(self) -> int:
        return self._exit_sign_id

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def distance_to_next(self) -> float:
        return self._distance_to_next

    @property
    def confidence_score(self) -> float:
        return self._confidence_score

    @confidence_score.setter
    def confidence_score(self, value: float) -> None:
        self._confidence_score = value

    @property
    def urgency(self) -> UrgencyLevel:
        return self._urgency

    @urgency.setter
    def urgency(self, value: UrgencyLevel) -> None:
        self._urgency = value

    def serialize(self) -> bytes:
        payload = {
            "type": self._message_type.value,
            "timestamp": self._timestamp.isoformat(),
            "exit_sign_id": self._exit_sign_id,
            "direction": self._direction.value,
            "distance_to_next": self._distance_to_next,
            "confidence_score": self._confidence_score,
            "urgency": self._urgency.value,
        }
        return json.dumps(payload).encode("utf-8")

    def get_network_packet(self) -> bytes:
        """Return a compact binary-style packet (here using serialized JSON with a header byte)."""
        header = b"\x01"  # packet type byte
        return header + self.serialize()

    def __repr__(self) -> str:
        return (
            f"RouteUpdateMessage(sign={self._exit_sign_id}, dir={self._direction}, "
            f"dist={self._distance_to_next:.2f}, urgency={self._urgency})"
        )
