from enum import Enum


class VertexType(Enum):
    ROOM = "ROOM"
    INTERSECTION = "INTERSECTION"
    EXIT = "EXIT"
    ASSEMBLY_POINT = "ASSEMBLY_POINT"
    REFUGE_AREA = "REFUGE_AREA"
    STAIRWELL = "STAIRWELL"
