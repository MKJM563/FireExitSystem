import json

from src.messaging.message import Message
from src.messaging.message_type import MessageType


class FireStatusMessage(Message):
    def __init__(self, device_id: int, vertex_id: int, fire_detected: bool, confidence: float = 1.0) -> None:
        super().__init__(MessageType.FIRE_STATUS)
        self._device_id: int = device_id
        self._vertex_id: int = vertex_id
        self._fire_detected: bool = fire_detected
        self._confidence: float = confidence

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def vertex_id(self) -> int:
        return self._vertex_id

    @property
    def fire_detected(self) -> bool:
        return self._fire_detected

    @property
    def confidence(self) -> float:
        return self._confidence

    def serialize(self) -> bytes:
        payload = {
            "type": self._message_type.value,
            "timestamp": self._timestamp.isoformat(),
            "device_id": self._device_id,
            "vertex_id": self._vertex_id,
            "fire_detected": self._fire_detected,
            "confidence": self._confidence,
        }
        return json.dumps(payload).encode("utf-8")

    def __repr__(self) -> str:
        return (
            f"FireStatusMessage(device={self._device_id}, vertex={self._vertex_id}, "
            f"fire={self._fire_detected}, confidence={self._confidence:.2f})"
        )
