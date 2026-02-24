import json

from src.messaging.message import Message
from src.messaging.message_type import MessageType
from src.hazard.device_type import DeviceType


class DeviceDownMessage(Message):
    def __init__(self, device_id: int, device_type: DeviceType, vertex_id: int) -> None:
        super().__init__(MessageType.DEVICE_DOWN)
        self._device_id: int = device_id
        self._device_type: DeviceType = device_type
        self._vertex_id: int = vertex_id

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def device_type(self) -> DeviceType:
        return self._device_type

    @property
    def vertex_id(self) -> int:
        return self._vertex_id

    def serialize(self) -> bytes:
        payload = {
            "type": self._message_type.value,
            "timestamp": self._timestamp.isoformat(),
            "device_id": self._device_id,
            "device_type": self._device_type.value,
            "vertex_id": self._vertex_id,
        }
        return json.dumps(payload).encode("utf-8")

    def __repr__(self) -> str:
        return (
            f"DeviceDownMessage(device={self._device_id}, type={self._device_type}, "
            f"vertex={self._vertex_id})"
        )
