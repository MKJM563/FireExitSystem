"""
Demo: End-to-end route calculation from a room to the nearest exit.

This script demonstrates:
1. Parsing a floor plan YAML file into a BuildingGraph (with disk caching)
2. Looking up vertex IDs for rooms and exits
3. Calculating the shortest route from a room to the nearest exit
4. Runtime modifications (safety scores, edge status) with persistent caching
5. Restoring runtime state after simulated restart
"""

import time
from datetime import datetime
from src.graph.yaml_graph_builder import YamlGraphBuilder
from src.graph.graph_cache import GraphCache
from src.graph.vertex_type import VertexType
from src.graph.edge_status import EdgeStatus
from src.route.route_calculator import RouteCalculator
from src.thread.configuration import Configuration


def main():
    # Path to the floor plan YAML (created by floor_plan_editor.py)
    yaml_path = "fire-evacuation-system/dsl.yaml"

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Parse the YAML floor plan into a BuildingGraph (with caching)
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 1: Parsing floor plan YAML into graph")
    print("=" * 60)

    # Create a cache for persistent storage
    cache = GraphCache()

    # Check cache states
    initial_cache_valid = cache.is_cache_valid(yaml_path)
    has_runtime_state = cache.has_runtime_state(yaml_path)

    builder = YamlGraphBuilder()
    start_time = time.perf_counter()
    # Try to restore runtime state if it exists
    graph = builder.build_from_file(yaml_path, cache=cache, restore_runtime_state=True)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    print(f"Loaded: {graph}")
    print(f"  - Vertices: {graph.get_vertex_count()}")
    print(f"  - Edges: {graph.get_edge_count()}")
    if has_runtime_state:
        print(f"  - Cache: RUNTIME STATE RESTORED (with modifications)")
    elif initial_cache_valid:
        print(f"  - Cache: HIT (loaded from disk)")
    else:
        print(f"  - Cache: MISS (parsed YAML, cached to disk)")
    print(f"  - Load time: {elapsed_ms:.2f}ms")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Inspect the graph structure
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 2: Graph structure (label → vertex ID mapping)")
    print("=" * 60)

    # Show the mapping from YAML labels to integer vertex IDs
    print("\nVertex ID mappings:")
    for label, vid in sorted(builder._id_map.items(), key=lambda x: x[1]):
        vertex = graph.get_vertex(vid)
        if vertex:
            print(f"  {label:6} → ID {vid:2}  (type: {vertex.type.value})")

    # List all vertices by type
    print("\nVertices by type:")
    all_vertices = graph.get_all_vertices()

    rooms = [v for v in all_vertices if v.type == VertexType.ROOM]
    exits = [v for v in all_vertices if v.type == VertexType.EXIT]
    junctions = [v for v in all_vertices if v.type == VertexType.INTERSECTION]

    print(f"  Rooms ({len(rooms)}): {[v.id for v in rooms]}")
    print(f"  Exits ({len(exits)}): {[v.id for v in exits]}")
    print(f"  Junctions ({len(junctions)}): {[v.id for v in junctions]}")
    print()

    # Build label lookup
    id_to_label = {v: k for k, v in builder._id_map.items()}

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Show current edge states (may have modifications from previous run)
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 3: Current edge states")
    print("=" * 60)

    print("\nEdges with non-default values:")
    modified_count = 0
    for vertex in all_vertices:
        for edge in graph.get_neighbors(vertex.id):
            # Check if edge has been modified from defaults
            if edge.safety_score != 100.0 or edge.status != EdgeStatus.OPERATIONAL or edge.congestion_factor != 1.0:
                src_label = id_to_label.get(edge.source_id, f"?{edge.source_id}")
                dst_label = id_to_label.get(edge.dest_id, f"?{edge.dest_id}")
                print(f"  {src_label} → {dst_label}: safety={edge.safety_score:.1f}, "
                      f"status={edge.status.value}, congestion={edge.congestion_factor:.1f}")
                modified_count += 1

    if modified_count == 0:
        print("  (All edges at default values)")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Calculate routes BEFORE modifications
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 4: Routes from all rooms (BEFORE new modifications)")
    print("=" * 60)

    config = Configuration()
    calculator = RouteCalculator(graph, config)

    for room in rooms:
        room_label = id_to_label.get(room.id, f"Room{room.id}")
        route = calculator.calculate_route(room.id, VertexType.EXIT)

        if route:
            path_labels = [id_to_label.get(vid, f"?{vid}") for vid in route.vertex_path]
            exit_label = path_labels[-1] if path_labels else "?"
            print(f"  {room_label:6} → {exit_label:4} | Distance: {route.total_distance:6.2f}m | Path: {' → '.join(path_labels)}")
        else:
            print(f"  {room_label:6} → NO ROUTE FOUND")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Simulate runtime modifications (fire/hazard scenario)
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 5: Simulating fire/hazard - modifying edge weights")
    print("=" * 60)

    # Scenario: Fire detected near J1, affecting routes through that junction
    j1_id = builder.get_vertex_id("J1")
    j3_id = builder.get_vertex_id("J3")
    t3_id = builder.get_vertex_id("T3")

    print("\n🔥 SCENARIO: Fire detected near junction J1!")
    print("   - Reducing safety scores on edges from J1")
    print("   - Marking J1→T3 corridor as DEGRADED")
    print("   - Increasing congestion on J3 (people evacuating)")

    # Modify edges from J1 (simulating fire hazard)
    if j1_id:
        j1_vertex = graph.get_vertex(j1_id)
        if j1_vertex:
            j1_vertex.mark_as_hazard(datetime.now(), confidence=0.85)
            print(f"\n   Marked J1 as hazard (confidence: 85%)")

        for edge in graph.get_neighbors(j1_id):
            dst_label = id_to_label.get(edge.dest_id, f"?{edge.dest_id}")
            old_safety = edge.safety_score

            # Reduce safety score significantly for edges near fire
            edge.update_safety_score(30.0)

            # Mark the exit corridor as degraded
            if edge.dest_id == t3_id:
                edge.set_status(EdgeStatus.DEGRADED)
                print(f"   Edge J1→{dst_label}: safety {old_safety:.0f}→{edge.safety_score:.0f}, status→DEGRADED")
            else:
                print(f"   Edge J1→{dst_label}: safety {old_safety:.0f}→{edge.safety_score:.0f}")

    # Increase congestion at J3 (evacuation traffic)
    if j3_id:
        for edge in graph.get_neighbors(j3_id):
            dst_label = id_to_label.get(edge.dest_id, f"?{edge.dest_id}")
            edge.update_congestion(2.5)
            print(f"   Edge J3→{dst_label}: congestion→{edge.congestion_factor:.1f}")

    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 6: Recalculate routes AFTER modifications
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 6: Routes from all rooms (AFTER modifications)")
    print("=" * 60)

    # Need to create new calculator to pick up weight changes
    calculator = RouteCalculator(graph, config)

    for room in rooms:
        room_label = id_to_label.get(room.id, f"Room{room.id}")
        route = calculator.calculate_route(room.id, VertexType.EXIT)

        if route:
            path_labels = [id_to_label.get(vid, f"?{vid}") for vid in route.vertex_path]
            exit_label = path_labels[-1] if path_labels else "?"
            print(f"  {room_label:6} → {exit_label:4} | Distance: {route.total_distance:6.2f}m | Path: {' → '.join(path_labels)}")
        else:
            print(f"  {room_label:6} → NO ROUTE FOUND")
    print()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 7: Save runtime state to disk
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 7: Persisting runtime state to disk")
    print("=" * 60)

    cache.save_runtime_state(yaml_path, graph, builder._id_map)

    cache_info = cache.get_cache_info(yaml_path)
    print(f"\n   Runtime state saved!")
    if cache_info and "runtime_state" in cache_info:
        rs = cache_info["runtime_state"]
        print(f"   - Cache file: {rs['cache_path']}")
        print(f"   - Last modified: {rs['last_modified']}")
        print(f"   - Compatible with YAML: {rs['is_compatible']}")

    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print("\n💡 TIP: Run this demo again to see the runtime state restored!")
    print("   The modified safety scores and edge states will persist.")
    print("   To reset, delete the .graph_cache folder or call:")
    print("   cache.invalidate_runtime_state(yaml_path)")


if __name__ == "__main__":
    main()
