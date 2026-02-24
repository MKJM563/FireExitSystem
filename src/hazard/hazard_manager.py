from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, TYPE_CHECKING

from src.graph.building_graph import BuildingGraph
from src.graph.edge import Edge
from src.hazard.hazard import Hazard

if TYPE_CHECKING:
    pass


class HazardManager:
    def __init__(self, graph: BuildingGraph) -> None:
        self._active_hazards: Dict[int, Hazard] = {}
        self._graph: BuildingGraph = graph
        self._propagation_radius: int = 3
        self._spread_interval: timedelta = timedelta(seconds=30)

    def add_hazard(self, device_id: int, vertex_id: int, confidence: float) -> None:
        hazard = Hazard(device_id, vertex_id, confidence)
        self._active_hazards[device_id] = hazard
        vertex = self._graph.get_vertex(vertex_id)
        if vertex is not None:
            vertex.mark_as_hazard(datetime.now(), confidence)

    def remove_hazard(self, device_id: int) -> None:
        hazard = self._active_hazards.pop(device_id, None)
        if hazard is not None:
            hazard.deactivate()
            vertex = self._graph.get_vertex(hazard.vertex_id)
            if vertex is not None:
                vertex.clear_hazard()

    def update_hazard_spread(self) -> List[int]:
        """Spread all active hazards by one radius step; return list of newly affected vertex IDs."""
        newly_affected: List[int] = []
        for hazard in self._active_hazards.values():
            if hazard.is_active:
                hazard.spread_radius()
                newly_affected.extend(hazard.get_affected_vertices(self._graph))
        return list(set(newly_affected))

    def get_affected_edges(self, hazard_vertex_id: int) -> List[Edge]:
        """Return all edges originating from hazard_vertex_id."""
        return self._graph.get_neighbors(hazard_vertex_id)

    def apply_hazard_weights(self) -> None:
        """Update safety scores on edges near all active hazards."""
        for hazard in self._active_hazards.values():
            if not hazard.is_active:
                continue
            affected_vertices = hazard.get_affected_vertices(self._graph)
            for i, vertex_id in enumerate(affected_vertices):
                distance = min(i, hazard.current_radius)
                score = self._calculate_safety_score(distance, hazard.confidence)
                for edge in self._graph.get_neighbors(vertex_id):
                    edge.update_safety_score(score)

    def _calculate_safety_score(self, distance: int, confidence: float) -> float:
        """score = max(0, 100 - (confidence * (100 / (distance + 1))))"""
        return max(0.0, 100.0 - (confidence * (100.0 / (distance + 1))))
