from datetime import datetime, timedelta

from src.hazard.operational_status import OperationalStatus
from src.hazard.device_type import DeviceType


class DeviceStatus:
    def __init__(self, device_id: int, device_type: DeviceType, status: OperationalStatus) -> None:
        self._device_id: int = device_id
        self._device_type: DeviceType = device_type
        self._status: OperationalStatus = status
        self._last_update_time: datetime = datetime.now()
        self._vertex_id: int = -1

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def device_type(self) -> DeviceType:
        return self._device_type

    @property
    def status(self) -> OperationalStatus:
        return self._status

    @status.setter
    def status(self, value: OperationalStatus) -> None:
        self._status = value
        self._last_update_time = datetime.now()

    @property
    def vertex_id(self) -> int:
        return self._vertex_id

    @vertex_id.setter
    def vertex_id(self, value: int) -> None:
        self._vertex_id = value

    def is_operational(self) -> bool:
        return self._status == OperationalStatus.OPERATIONAL

    def is_failed(self) -> bool:
        return self._status in (OperationalStatus.ERROR, OperationalStatus.OFFLINE)

    def get_time_since_update(self) -> timedelta:
        return datetime.now() - self._last_update_time

    def __repr__(self) -> str:
        return f"DeviceStatus(id={self._device_id}, type={self._device_type}, status={self._status})"
