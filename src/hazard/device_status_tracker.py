from typing import Dict, List, Optional

from src.hazard.device_status import DeviceStatus
from src.hazard.device_type import DeviceType
from src.hazard.operational_status import OperationalStatus


class DeviceStatusTracker:
    def __init__(self) -> None:
        self._device_statuses: Dict[int, DeviceStatus] = {}
        self._vertex_to_device_map: Dict[int, List[int]] = {}

    def update_device_status(self, device_id: int, status: DeviceStatus) -> None:
        self._device_statuses[device_id] = status
        vertex_id = status.vertex_id
        if vertex_id >= 0:
            if vertex_id not in self._vertex_to_device_map:
                self._vertex_to_device_map[vertex_id] = []
            if device_id not in self._vertex_to_device_map[vertex_id]:
                self._vertex_to_device_map[vertex_id].append(device_id)

    def get_device_status(self, device_id: int) -> Optional[DeviceStatus]:
        return self._device_statuses.get(device_id)

    def get_devices_at_vertex(self, vertex_id: int) -> List[int]:
        return list(self._vertex_to_device_map.get(vertex_id, []))

    def get_failed_devices(self) -> List[int]:
        return [
            device_id
            for device_id, status in self._device_statuses.items()
            if status.is_failed()
        ]

    def is_device_operational(self, device_id: int) -> bool:
        status = self._device_statuses.get(device_id)
        if status is None:
            return False
        return status.is_operational()
