from __future__ import annotations
import heapq
from typing import Dict, List, Optional, TYPE_CHECKING

from src.graph.building_graph import BuildingGraph
from src.graph.vertex_type import VertexType
from src.graph.accessibility_flags import AccessibilityFlags
from src.graph.edge import Edge
from src.route.route import Route
from src.route.weight_factors import WeightFactors
from src.route.routing_mode import RoutingMode

if TYPE_CHECKING:
    from src.thread.configuration import Configuration


class RouteCalculator:
    def __init__(self, graph: BuildingGraph, config: "Configuration") -> None:
        self._graph: BuildingGraph = graph
        self._routing_mode: RoutingMode = config.routing_mode
        self._weight_factors: WeightFactors = WeightFactors.get_preset(self._routing_mode)

    def calculate_route(self, start_vertex_id: int, target_type: VertexType) -> Optional[Route]:
        return self._dijkstra_algorithm(start_vertex_id, target_type)

    def calculate_all_routes(self, exit_sign_vertices: List[int]) -> Dict[int, Route]:
        routes: Dict[int, Route] = {}
        for vertex_id in exit_sign_vertices:
            route = self.calculate_route(vertex_id, VertexType.EXIT)
            if route is not None:
                routes[vertex_id] = route
        return routes

    def set_routing_mode(self, mode: RoutingMode) -> None:
        self._routing_mode = mode
        self._weight_factors = WeightFactors.get_preset(mode)

    def set_weight_factors(self, factors: WeightFactors) -> None:
        self._weight_factors = factors

    def _dijkstra_algorithm(self, start: int, target_type: VertexType) -> Optional[Route]:
        """Standard Dijkstra using heapq, finding the nearest vertex of targetType."""
        distances: Dict[int, float] = {start: 0.0}
        previous: Dict[int, Optional[int]] = {start: None}
        # heap entries: (cost, vertex_id)
        heap: List[tuple] = [(0.0, start)]

        while heap:
            cost, current = heapq.heappop(heap)

            if cost > distances.get(current, float("inf")):
                continue  # stale entry

            vertex = self._graph.get_vertex(current)
            if vertex is not None and vertex.type == target_type and current != start:
                path = self._reconstruct_path(previous, current)
                return Route(path, distances[current])

            for edge in self._filter_by_accessibility(self._graph.get_neighbors(current)):
                if not edge.is_passable():
                    continue
                neighbor = edge.dest_id
                new_cost = cost + edge.calculate_composite_weight(self._weight_factors)
                if new_cost < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_cost
                    previous[neighbor] = current
                    heapq.heappush(heap, (new_cost, neighbor))

        return None  # no path found

    def _reconstruct_path(self, previous: Dict[int, Optional[int]], end: int) -> List[int]:
        path: List[int] = []
        current: Optional[int] = end
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        return path

    def _filter_by_accessibility(self, edges: List[Edge]) -> List[Edge]:
        """For ACCESSIBILITY mode, filter edges that satisfy wheelchair requirements."""
        if self._routing_mode != RoutingMode.ACCESSIBILITY:
            return edges
        requirements = AccessibilityFlags(wheelchair=True, stretcher=False, general=True)
        return [e for e in edges if e.is_accessible(requirements)]
