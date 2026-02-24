from enum import Enum


class EdgeStatus(Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"
    IMPASSABLE = "IMPASSABLE"
