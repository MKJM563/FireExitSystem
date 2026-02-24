from src.graph.vertex_type import VertexType
from src.route.routing_mode import RoutingMode


class RouteCacheKey:
    def __init__(self, start_vertex_id: int, target_type: VertexType, routing_mode: RoutingMode) -> None:
        self._start_vertex_id: int = start_vertex_id
        self._target_type: VertexType = target_type
        self._routing_mode: RoutingMode = routing_mode

    @property
    def start_vertex_id(self) -> int:
        return self._start_vertex_id

    @property
    def target_type(self) -> VertexType:
        return self._target_type

    @property
    def routing_mode(self) -> RoutingMode:
        return self._routing_mode

    def equals(self, other: "RouteCacheKey") -> bool:
        return (
            self._start_vertex_id == other._start_vertex_id
            and self._target_type == other._target_type
            and self._routing_mode == other._routing_mode
        )

    def hash_code(self) -> int:
        return hash((self._start_vertex_id, self._target_type, self._routing_mode))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RouteCacheKey):
            return False
        return self.equals(other)

    def __hash__(self) -> int:
        return self.hash_code()

    def __repr__(self) -> str:
        return f"RouteCacheKey(start={self._start_vertex_id}, target={self._target_type}, mode={self._routing_mode})"
