from enum import Enum


class OperationalStatus(Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"
