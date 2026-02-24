import math
import sys
import yaml
import networkx as nx


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def build_graph_from_dsl(dsl):
    G = nx.Graph()

    # Junctions
    for j in dsl.get("junctions", []):
        G.add_node(
            j["id"],
            pos=tuple(j["position"]),
            type="junction"
        )

    # Terminals
    for t in dsl.get("terminals", []):
        G.add_node(
            t["id"],
            pos=tuple(t["position"]),
            type="terminal"
        )

    pos_map = {
        n: data["pos"]
        for n, data in G.nodes(data=True)
        if "pos" in data
    }

    # Corridors (superedges)
    for c in dsl.get("corridors", []):
        from_id = c["from"]
        to_id = c["to"]
        length = c.get("length")
        if length is None and from_id in pos_map and to_id in pos_map:
            length = distance(pos_map[from_id], pos_map[to_id])
        if length is None:
            length = 1.0

        G.add_edge(
            from_id,
            to_id,
            weight=float(length),
            type="corridor"
        )

    # Rooms + portals
    for r in dsl.get("rooms", []):
        portal = f"P_{r['id']}"

        G.add_node(portal, type="portal")
        G.add_node(r["id"], type="room")

        G.add_edge(
            portal,
            r["id"],
            weight=r.get("door_cost", 1.0),
            type="door"
        )

        # Only create portal link if room is attached to a junction
        if r.get("attached_to"):
            G.add_edge(
                portal,
                r["attached_to"],
                weight=0.5,
                type="portal_link"
            )

    # Fire exit signs
    for fe in dsl.get("fire_exits", []):
        node_id = fe["attached_to"]
        if node_id in G:
            if "fire_exit" not in G.nodes[node_id]:
                G.nodes[node_id]["fire_exit"] = []
            G.nodes[node_id]["fire_exit"].append(fe["id"])

    # Room-to-room connections
    for rc in dsl.get("room_connections", []):
        room1 = rc["from"]
        room2 = rc["to"]
        cost = rc.get("cost", 1.0)
        
        if room1 in G and room2 in G:
            G.add_edge(
                room1,
                room2,
                weight=float(cost),
                type="room_connection"
            )

    return G


def closest_terminal(G, start_room, terminals):
    if start_room not in G:
        raise ValueError(f"Unknown room: {start_room}")

    best_terminal = None
    best_distance = None
    best_path = None

    for t in terminals:
        if t not in G:
            continue
        try:
            dist = nx.shortest_path_length(G, start_room, t, weight="weight")
            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_terminal = t
                best_path = nx.shortest_path(G, start_room, t, weight="weight")
        except nx.NetworkXNoPath:
            continue

    return best_terminal, best_distance, best_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python nearest_terminal.py <dsl.yaml> <room_id>")
        sys.exit(1)

    dsl_path = sys.argv[1]
    room_id = sys.argv[2]

    with open(dsl_path) as f:
        dsl = yaml.safe_load(f)

    G = build_graph_from_dsl(dsl)

    terminals = [t["id"] for t in dsl.get("terminals", [])]
    terminal, distance, path = closest_terminal(G, room_id, terminals)

    if terminal is None:
        print(f"No reachable terminal from {room_id}.")
        sys.exit(2)

    print(f"Closest terminal: {terminal}")
    print(f"Total cost: {distance:.2f}")
    print("Path:")
    print(" -> ".join(path))
    
    # Check for fire exit signs along the path
    fire_exits_on_path = []
    for node in path:
        if "fire_exit" in G.nodes[node]:
            fire_exits_on_path.extend(G.nodes[node]["fire_exit"])
    
    if fire_exits_on_path:
        print(f"Fire exit signs on path: {', '.join(fire_exits_on_path)}")


if __name__ == "__main__":
    main()
