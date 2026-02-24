from __future__ import annotations
import threading
from typing import Dict, List, Optional

from src.graph.vertex import Vertex
from src.graph.edge import Edge
from src.graph.edge_key import EdgeKey


class BuildingGraph:
    def __init__(self) -> None:
        self._vertices: Dict[int, Vertex] = {}
        self._edges: Dict[EdgeKey, Edge] = {}
        self._adjacency_list: Dict[int, List[Edge]] = {}
        self._device_to_vertex_map: Dict[int, int] = {}
        self._lock: threading.RLock = threading.RLock()

    def add_vertex(self, vertex: Vertex) -> None:
        with self._lock:
            self._vertices[vertex.id] = vertex
            if vertex.id not in self._adjacency_list:
                self._adjacency_list[vertex.id] = []
            for device_id in vertex.get_device_ids():
                self._device_to_vertex_map[device_id] = vertex.id

    def add_edge(self, edge: Edge) -> None:
        with self._lock:
            key = EdgeKey(edge.source_id, edge.dest_id)
            self._edges[key] = edge
            if edge.source_id not in self._adjacency_list:
                self._adjacency_list[edge.source_id] = []
            self._adjacency_list[edge.source_id].append(edge)

    def get_vertex(self, id: int) -> Optional[Vertex]:
        with self._lock:
            return self._vertices.get(id)

    def get_edge(self, source_id: int, dest_id: int) -> Optional[Edge]:
        with self._lock:
            return self._edges.get(EdgeKey(source_id, dest_id))

    def get_neighbors(self, vertex_id: int) -> List[Edge]:
        with self._lock:
            return list(self._adjacency_list.get(vertex_id, []))

    def get_vertex_by_device(self, device_id: int) -> Optional[Vertex]:
        with self._lock:
            vertex_id = self._device_to_vertex_map.get(device_id)
            if vertex_id is None:
                return None
            return self._vertices.get(vertex_id)

    def register_device(self, device_id: int, vertex_id: int) -> None:
        """Register a device-to-vertex mapping (used outside of add_vertex)."""
        with self._lock:
            self._device_to_vertex_map[device_id] = vertex_id

    def lock_for_read(self) -> None:
        self._lock.acquire()

    def lock_for_write(self) -> None:
        self._lock.acquire()

    def unlock(self) -> None:
        self._lock.release()

    def get_vertex_count(self) -> int:
        with self._lock:
            return len(self._vertices)

    def get_edge_count(self) -> int:
        with self._lock:
            return len(self._edges)

    def get_all_vertices(self) -> List[Vertex]:
        with self._lock:
            return list(self._vertices.values())

    def __repr__(self) -> str:
        return f"BuildingGraph(vertices={len(self._vertices)}, edges={len(self._edges)})"
