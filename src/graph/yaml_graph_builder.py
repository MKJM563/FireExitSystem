from __future__ import annotations

from typing import Dict, Optional

import yaml

from src.graph.building_graph import BuildingGraph
from src.graph.edge import Edge
from src.graph.vertex import Vertex
from src.graph.vertex_type import VertexType


class YamlGraphBuilder:
    """Build a :class:`BuildingGraph` from a floor-plan DSL YAML produced by
    :class:`FloorPlanEditor`.

    The YAML format contains:

    * ``junctions``      – corridor intersections  → :attr:`VertexType.INTERSECTION`
    * ``terminals``      – building exits           → :attr:`VertexType.EXIT`
    * ``rooms``          – occupiable rooms         → :attr:`VertexType.ROOM`
    * ``corridors``      – walkable paths between nodes
    * ``room_connections`` – direct room-to-room links
    * ``fire_exits``     – fire-exit signs attached to nodes

    String node labels (e.g. ``"J1"``, ``"T2"``) are mapped to sequential
    integer vertex IDs so that the :class:`BuildingGraph` can be used
    directly by the route-processing thread.
    """

    def __init__(self) -> None:
        # Integer IDs start at 1 and are scoped to this builder instance.
        # Each builder maintains its own isolated label→int namespace, so
        # multiple builders never produce conflicting IDs for the same graph.
        self._id_map: Dict[str, int] = {}
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_vertex_id(self, label: str) -> Optional[int]:
        """Return the integer vertex ID assigned to *label*, or ``None``."""
        return self._id_map.get(label)

    # ------------------------------------------------------------------
    # Build from file / dict
    # ------------------------------------------------------------------

    def build_from_file(self, yaml_path: str) -> BuildingGraph:
        """Parse *yaml_path* and return the corresponding :class:`BuildingGraph`."""
        with open(yaml_path) as fh:
            data = yaml.safe_load(fh)
        return self.build_from_dict(data)

    def build_from_dict(self, data: dict) -> BuildingGraph:
        """Build a :class:`BuildingGraph` from the parsed DSL *data* dictionary."""
        graph = BuildingGraph()
        floor = 0  # single-floor per system requirements

        # ---- junctions → INTERSECTION --------------------------------
        for j in data.get("junctions", []):
            vid = self._assign_id(j["id"])
            x, y = j["position"]
            graph.add_vertex(Vertex(vid, float(x), float(y), floor, VertexType.INTERSECTION))

        # ---- terminals → EXIT ----------------------------------------
        for t in data.get("terminals", []):
            vid = self._assign_id(t["id"])
            x, y = t["position"]
            graph.add_vertex(Vertex(vid, float(x), float(y), floor, VertexType.EXIT))

        # ---- rooms → ROOM (with optional portal link) ----------------
        for r in data.get("rooms", []):
            vid = self._assign_id(r["id"])
            # Rooms have no explicit position in the DSL YAML export; their
            # spatial centre is stored only in the editor's in-memory state.
            # (0.0, 0.0) is used as a placeholder – route calculations rely on
            # edge weights rather than vertex coordinates.
            graph.add_vertex(Vertex(vid, 0.0, 0.0, floor, VertexType.ROOM))

            attached = r.get("attached_to")
            if attached:
                junction_vid = self._assign_id(attached)
                door_cost = float(r.get("door_cost", 1.0))
                # Bidirectional door edge between room and its junction.
                graph.add_edge(Edge(vid, junction_vid, door_cost))
                graph.add_edge(Edge(junction_vid, vid, door_cost))

        # ---- corridors → bidirectional edges -------------------------
        for c in data.get("corridors", []):
            src = self._assign_id(c["from"])
            dst = self._assign_id(c["to"])
            length = float(c.get("length", 1.0))
            graph.add_edge(Edge(src, dst, length))
            graph.add_edge(Edge(dst, src, length))

        # ---- room-to-room connections → bidirectional edges ----------
        for rc in data.get("room_connections", []):
            src = self._assign_id(rc["from"])
            dst = self._assign_id(rc["to"])
            cost = float(rc.get("cost", 1.0))
            graph.add_edge(Edge(src, dst, cost))
            graph.add_edge(Edge(dst, src, cost))

        # ---- fire-exit signs → device IDs on their host vertex -------
        for fe in data.get("fire_exits", []):
            fe_device_id = self._assign_id(fe["id"])
            host_vid = self._assign_id(fe["attached_to"])
            vertex = graph.get_vertex(host_vid)
            if vertex is not None:
                vertex.add_device(fe_device_id)

        return graph

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assign_id(self, label: str) -> int:
        """Return existing or freshly assigned integer ID for *label*."""
        if label not in self._id_map:
            self._id_map[label] = self._next_id
            self._next_id += 1
        return self._id_map[label]
