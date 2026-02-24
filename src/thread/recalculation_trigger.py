from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING

from src.thread.trigger_type import TriggerType

if TYPE_CHECKING:
    from src.graph.building_graph import BuildingGraph
    from src.graph.vertex_type import VertexType


class RecalculationTrigger:
    def __init__(self, trigger_type: TriggerType, vertices: List[int]) -> None:
        self._trigger_type: TriggerType = trigger_type
        self._affected_vertices: List[int] = list(vertices)
        self._priority: int = self._default_priority(trigger_type)
        self._timestamp: datetime = datetime.now()

    @property
    def trigger_type(self) -> TriggerType:
        return self._trigger_type

    @property
    def affected_vertices(self) -> List[int]:
        return list(self._affected_vertices)

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def is_full_recalculation(self) -> bool:
        return self._trigger_type in (TriggerType.MANUAL, TriggerType.PERIODIC)

    def get_affected_exit_signs(self, graph: "BuildingGraph") -> List[int]:
        """Return vertices of type EXIT_SIGN (here EXIT) near affected vertices."""
        from src.graph.vertex_type import VertexType
        if self.is_full_recalculation():
            return [v.id for v in graph.get_all_vertices() if v.type == VertexType.EXIT]
        # Return exit vertices reachable within 1 hop of affected vertices
        exit_signs: List[int] = []
        for vertex_id in self._affected_vertices:
            vertex = graph.get_vertex(vertex_id)
            if vertex is not None and vertex.type == VertexType.EXIT:
                exit_signs.append(vertex_id)
            for edge in graph.get_neighbors(vertex_id):
                neighbor = graph.get_vertex(edge.dest_id)
                if neighbor is not None and neighbor.type == VertexType.EXIT:
                    exit_signs.append(neighbor.id)
        return list(set(exit_signs))

    @staticmethod
    def _default_priority(trigger_type: TriggerType) -> int:
        priorities = {
            TriggerType.FIRE_DETECTION: 10,
            TriggerType.DEVICE_FAILURE: 7,
            TriggerType.HAZARD_SPREAD: 8,
            TriggerType.MANUAL: 5,
            TriggerType.PERIODIC: 1,
        }
        return priorities.get(trigger_type, 5)

    def __repr__(self) -> str:
        return (
            f"RecalculationTrigger(type={self._trigger_type}, "
            f"vertices={self._affected_vertices}, priority={self._priority})"
        )
