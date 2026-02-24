"""
Tests for the RouteProcessingThread and its supporting components.

Graph layout used in the tests (single floor, coordinates in metres):

    (1) ROOM ──10m──► (2) INTERSECTION ──5m──► (3) EXIT
                              │
                              8m
                              ▼
                           (4) EXIT

    Smoke alarm  device_id=101 is at vertex 1.
    Exit sign    device_id=201 is at vertex 3.
    Exit sign    device_id=202 is at vertex 4.

This topology exercises:
  - Normal routing (find nearest exit from each exit-sign vertex).
  - Fire detection  → hazard marking → safety-score degradation → rerouting.
  - Device-down     → device status tracked.
  - Manual trigger  → full recalculation.
  - Route caching   → cache hits and invalidation.
  - Full thread lifecycle (start / enqueue / dequeue / stop).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from typing import List

import pytest
import yaml

from src.graph.building_graph import BuildingGraph
from src.graph.edge import Edge
from src.graph.edge_status import EdgeStatus
from src.graph.vertex import Vertex
from src.graph.vertex_type import VertexType
from src.graph.accessibility_flags import AccessibilityFlags
from src.graph.yaml_graph_builder import YamlGraphBuilder
from src.hazard.device_type import DeviceType
from src.hazard.hazard_manager import HazardManager
from src.hazard.device_status_tracker import DeviceStatusTracker
from src.hazard.operational_status import OperationalStatus
from src.messaging.device_down_message import DeviceDownMessage
from src.messaging.fire_status_message import FireStatusMessage
from src.messaging.message_type import MessageType
from src.messaging.message_queue import MessageQueue
from src.messaging.route_update_message import RouteUpdateMessage
from src.route.route import Route
from src.route.route_cache import RouteCache
from src.route.route_calculator import RouteCalculator
from src.route.routing_mode import RoutingMode
from src.route.weight_factors import WeightFactors
from src.thread.configuration import Configuration
from src.thread.recalculation_trigger import RecalculationTrigger
from src.thread.route_processing_thread import RouteProcessingThread
from src.thread.trigger_type import TriggerType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_graph() -> BuildingGraph:
    """Build the test topology described in the module docstring."""
    graph = BuildingGraph()

    v1 = Vertex(1, 0.0, 0.0, 0, VertexType.ROOM)
    v1.add_device(101)  # smoke alarm
    v2 = Vertex(2, 10.0, 0.0, 0, VertexType.INTERSECTION)
    v3 = Vertex(3, 15.0, 0.0, 0, VertexType.EXIT)
    v3.add_device(201)  # exit sign
    v4 = Vertex(4, 10.0, -8.0, 0, VertexType.EXIT)
    v4.add_device(202)  # exit sign

    for v in (v1, v2, v3, v4):
        graph.add_vertex(v)

    graph.add_edge(Edge(1, 2, 10.0))
    graph.add_edge(Edge(2, 3, 5.0))
    graph.add_edge(Edge(2, 4, 8.0))

    return graph


def _make_config() -> Configuration:
    config = Configuration()
    config._routing_mode = RoutingMode.SAFETY_FIRST
    config._weight_factors = WeightFactors.get_preset(RoutingMode.SAFETY_FIRST)
    config._cache_size = 50
    config._recalculation_debounce_ms = 0   # no debounce in tests
    config._spread_interval_seconds = 3600  # delay periodic recalculation during tests
    return config


def _drain_output(thread: RouteProcessingThread, timeout: float = 1.0) -> List[RouteUpdateMessage]:
    """Collect all RouteUpdateMessage objects from the output queue within *timeout* seconds."""
    deadline = time.monotonic() + timeout
    results: List[RouteUpdateMessage] = []
    while time.monotonic() < deadline:
        msg = thread.output_queue.dequeue()
        if msg is None:
            time.sleep(0.02)
            continue
        if isinstance(msg, RouteUpdateMessage):
            results.append(msg)
    return results


# ---------------------------------------------------------------------------
# Graph data-structure tests
# ---------------------------------------------------------------------------

class TestBuildingGraph:
    def test_vertex_lookup_by_id(self):
        graph = _make_graph()
        assert graph.get_vertex(1) is not None
        assert graph.get_vertex(1).type == VertexType.ROOM
        assert graph.get_vertex(999) is None

    def test_vertex_count(self):
        graph = _make_graph()
        assert graph.get_vertex_count() == 4

    def test_edge_count(self):
        graph = _make_graph()
        assert graph.get_edge_count() == 3

    def test_edge_lookup(self):
        graph = _make_graph()
        edge = graph.get_edge(1, 2)
        assert edge is not None
        assert edge.base_distance == 10.0

    def test_missing_edge_lookup(self):
        graph = _make_graph()
        assert graph.get_edge(3, 1) is None

    def test_adjacency_list(self):
        graph = _make_graph()
        neighbors = graph.get_neighbors(2)
        dest_ids = {e.dest_id for e in neighbors}
        assert dest_ids == {3, 4}

    def test_device_to_vertex_mapping(self):
        graph = _make_graph()
        v = graph.get_vertex_by_device(101)
        assert v is not None
        assert v.id == 1

    def test_get_all_vertices(self):
        graph = _make_graph()
        ids = {v.id for v in graph.get_all_vertices()}
        assert ids == {1, 2, 3, 4}


# ---------------------------------------------------------------------------
# Vertex tests
# ---------------------------------------------------------------------------

class TestVertex:
    def test_mark_and_clear_hazard(self):
        from datetime import datetime
        v = Vertex(10, 1.0, 2.0, 0, VertexType.ROOM)
        assert not v.is_hazard
        v.mark_as_hazard(datetime.now(), confidence=0.9)
        assert v.is_hazard
        assert v.hazard_confidence == pytest.approx(0.9)
        v.clear_hazard()
        assert not v.is_hazard
        assert v.hazard_confidence == 0.0

    def test_add_remove_device(self):
        v = Vertex(11, 0.0, 0.0, 0, VertexType.ROOM)
        v.add_device(55)
        assert 55 in v.get_device_ids()
        v.remove_device(55)
        assert 55 not in v.get_device_ids()

    def test_accessibility(self):
        v = Vertex(12, 0.0, 0.0, 0, VertexType.ROOM)
        req = AccessibilityFlags(wheelchair=True, stretcher=False, general=True)
        # Default flags allow wheelchair + general
        assert v.is_accessible(req)


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------

class TestEdge:
    def test_default_passable(self):
        e = Edge(1, 2, 5.0)
        assert e.is_passable()

    def test_blocked_not_passable(self):
        e = Edge(1, 2, 5.0)
        e.set_status(EdgeStatus.BLOCKED)
        assert not e.is_passable()

    def test_impassable_not_passable(self):
        e = Edge(1, 2, 5.0)
        e.set_status(EdgeStatus.IMPASSABLE)
        assert not e.is_passable()

    def test_composite_weight(self):
        e = Edge(1, 2, 10.0)
        wf = WeightFactors(0.5, 0.3, 0.2)
        # weight = 0.5*10 + 0.3*(100-100) + 0.2*1 = 5.0 + 0.0 + 0.2 = 5.2
        assert e.calculate_composite_weight(wf) == pytest.approx(5.2)

    def test_safety_score_update(self):
        e = Edge(1, 2, 5.0)
        e.update_safety_score(50.0)
        assert e.safety_score == pytest.approx(50.0)

    def test_safety_score_clamped(self):
        e = Edge(1, 2, 5.0)
        e.update_safety_score(150.0)
        assert e.safety_score == pytest.approx(100.0)
        e.update_safety_score(-10.0)
        assert e.safety_score == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Route-calculation tests
# ---------------------------------------------------------------------------

class TestRouteCalculator:
    def setup_method(self):
        self.graph = _make_graph()
        self.config = _make_config()
        self.calculator = RouteCalculator(self.graph, self.config)

    def test_route_from_exit_sign_to_nearest_exit(self):
        # Vertex 3 is already an EXIT, so routing from vertex 2 (INTERSECTION) to EXIT
        # should find vertex 3 (distance 5) before vertex 4 (distance 8).
        route = self.calculator.calculate_route(2, VertexType.EXIT)
        assert route is not None
        assert route.is_valid()
        assert route.vertex_path[-1] == 3  # nearest exit is vertex 3

    def test_route_returns_none_when_no_path(self):
        # Isolated vertex with no edges to an EXIT
        self.graph.add_vertex(Vertex(99, 99.0, 99.0, 0, VertexType.ROOM))
        route = self.calculator.calculate_route(99, VertexType.EXIT)
        assert route is None

    def test_blocked_edge_excluded(self):
        # Block the edge from 2→3, so the only route is 2→4
        edge = self.graph.get_edge(2, 3)
        edge.set_status(EdgeStatus.BLOCKED)
        route = self.calculator.calculate_route(2, VertexType.EXIT)
        assert route is not None
        assert route.vertex_path[-1] == 4

    def test_calculate_all_routes(self):
        routes = self.calculator.calculate_all_routes([2])
        assert 2 in routes
        assert routes[2].is_valid()

    def test_routing_mode_switch(self):
        self.calculator.set_routing_mode(RoutingMode.SPEED)
        route = self.calculator.calculate_route(2, VertexType.EXIT)
        assert route is not None


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

class TestRoute:
    def test_valid_route(self):
        r = Route([1, 2, 3], 15.0)
        assert r.is_valid()

    def test_single_vertex_route_invalid(self):
        r = Route([1], 0.0)
        assert not r.is_valid()

    def test_get_next_vertex(self):
        r = Route([1, 2, 3], 15.0)
        assert r.get_next_vertex(1) == 2
        assert r.get_next_vertex(2) == 3
        assert r.get_next_vertex(3) is None

    def test_confidence_score(self):
        r = Route([1, 2], 5.0)
        r.set_confidence_score(0.75)
        assert r.get_confidence_score() == pytest.approx(0.75)

    def test_confidence_score_clamped(self):
        r = Route([1, 2], 5.0)
        r.set_confidence_score(2.0)
        assert r.get_confidence_score() == pytest.approx(1.0)
        r.set_confidence_score(-1.0)
        assert r.get_confidence_score() == pytest.approx(0.0)

    def test_distance_to_next(self):
        r = Route([1, 2, 3], 15.0)
        # 15.0 / 2 segments = 7.5
        assert r.get_distance_to_next(1) == pytest.approx(7.5)

    def test_get_direction_with_positions(self):
        from src.route.direction import Direction
        positions = {1: (0.0, 0.0), 2: (0.0, 10.0)}  # due North
        r = Route([1, 2], 10.0, vertex_positions=positions)
        direction = r.get_direction(1, 0.0)
        assert direction == Direction.NORTH


# ---------------------------------------------------------------------------
# Route-cache tests
# ---------------------------------------------------------------------------

class TestRouteCache:
    def test_cache_miss(self):
        cache = RouteCache(10)
        result = cache.get(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST)
        assert result is None

    def test_cache_put_and_get(self):
        cache = RouteCache(10)
        route = Route([1, 3], 15.0)
        cache.put(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST, route)
        result = cache.get(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST)
        assert result is route

    def test_cache_invalidate(self):
        cache = RouteCache(10)
        route = Route([1, 3], 15.0)
        cache.put(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST, route)
        cache.invalidate(1, radius=0)
        assert cache.get(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST) is None

    def test_cache_invalidate_all(self):
        cache = RouteCache(10)
        cache.put(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST, Route([1, 3], 15.0))
        cache.put(2, VertexType.EXIT, RoutingMode.SAFETY_FIRST, Route([2, 3], 5.0))
        cache.invalidate_all()
        assert cache.get_size() == 0

    def test_cache_lru_eviction(self):
        cache = RouteCache(2)
        r1 = Route([1, 3], 15.0)
        r2 = Route([2, 3], 5.0)
        r3 = Route([2, 4], 8.0)
        cache.put(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST, r1)
        cache.put(2, VertexType.EXIT, RoutingMode.SAFETY_FIRST, r2)
        # Adding a third entry should evict the first (LRU)
        cache.put(2, VertexType.EXIT, RoutingMode.SPEED, r3)
        assert cache.get_size() == 2
        assert cache.get(1, VertexType.EXIT, RoutingMode.SAFETY_FIRST) is None


# ---------------------------------------------------------------------------
# Hazard-manager tests
# ---------------------------------------------------------------------------

class TestHazardManager:
    def setup_method(self):
        self.graph = _make_graph()
        self.manager = HazardManager(self.graph)

    def test_add_hazard_marks_vertex(self):
        self.manager.add_hazard(101, 1, 0.9)
        v = self.graph.get_vertex(1)
        assert v.is_hazard
        assert v.hazard_confidence == pytest.approx(0.9)

    def test_remove_hazard_clears_vertex(self):
        self.manager.add_hazard(101, 1, 0.9)
        self.manager.remove_hazard(101)
        v = self.graph.get_vertex(1)
        assert not v.is_hazard

    def test_hazard_spread_increases_radius(self):
        self.manager.add_hazard(101, 1, 0.8)
        affected = self.manager.update_hazard_spread()
        # After one spread the hazard radius is 1, so vertex 2 is now affected
        assert 1 in affected or 2 in affected

    def test_apply_hazard_weights_degrades_safety(self):
        self.manager.add_hazard(101, 1, 1.0)
        # Spread once so vertex 2 is in the hazard zone
        self.manager.update_hazard_spread()
        self.manager.apply_hazard_weights()
        # Edge 1→2 originates from hazard vertex 1; safety should be < 100
        edge = self.graph.get_edge(1, 2)
        assert edge.safety_score < 100.0

    def test_get_affected_edges(self):
        edges = self.manager.get_affected_edges(2)
        dest_ids = {e.dest_id for e in edges}
        assert dest_ids == {3, 4}


# ---------------------------------------------------------------------------
# DeviceStatusTracker tests
# ---------------------------------------------------------------------------

class TestDeviceStatusTracker:
    def test_update_and_retrieve_status(self):
        from src.hazard.device_status import DeviceStatus
        tracker = DeviceStatusTracker()
        ds = DeviceStatus(201, DeviceType.EXIT_SIGN, OperationalStatus.OFFLINE)
        tracker.update_device_status(201, ds)
        retrieved = tracker.get_device_status(201)
        assert retrieved is not None
        assert retrieved.is_failed()

    def test_is_device_operational(self):
        from src.hazard.device_status import DeviceStatus
        tracker = DeviceStatusTracker()
        ds = DeviceStatus(101, DeviceType.SMOKE_ALARM, OperationalStatus.OPERATIONAL)
        tracker.update_device_status(101, ds)
        assert tracker.is_device_operational(101)

    def test_get_failed_devices(self):
        from src.hazard.device_status import DeviceStatus
        tracker = DeviceStatusTracker()
        tracker.update_device_status(
            201,
            DeviceStatus(201, DeviceType.EXIT_SIGN, OperationalStatus.ERROR),
        )
        tracker.update_device_status(
            101,
            DeviceStatus(101, DeviceType.SMOKE_ALARM, OperationalStatus.OPERATIONAL),
        )
        failed = tracker.get_failed_devices()
        assert 201 in failed
        assert 101 not in failed


# ---------------------------------------------------------------------------
# Message tests
# ---------------------------------------------------------------------------

class TestMessages:
    def test_fire_status_message_type(self):
        msg = FireStatusMessage(101, 1, True, 0.95)
        assert msg.get_type() == MessageType.FIRE_STATUS
        assert msg.fire_detected
        assert msg.confidence == pytest.approx(0.95)

    def test_fire_status_serialize(self):
        import json
        msg = FireStatusMessage(101, 1, True)
        data = json.loads(msg.serialize())
        assert data["fire_detected"] is True
        assert data["device_id"] == 101

    def test_device_down_message_type(self):
        msg = DeviceDownMessage(201, DeviceType.EXIT_SIGN, 3)
        assert msg.get_type() == MessageType.DEVICE_DOWN
        assert msg.device_type == DeviceType.EXIT_SIGN

    def test_route_update_message_type(self):
        from src.route.direction import Direction
        msg = RouteUpdateMessage(201, Direction.NORTH, 5.0)
        assert msg.get_type() == MessageType.ROUTE_UPDATE
        assert msg.exit_sign_id == 201


# ---------------------------------------------------------------------------
# MessageQueue tests
# ---------------------------------------------------------------------------

class TestMessageQueue:
    def test_enqueue_dequeue(self):
        mq = MessageQueue(10)
        msg = FireStatusMessage(1, 1, True)
        assert mq.enqueue(msg)
        result = mq.dequeue()
        assert result is msg

    def test_empty_dequeue_returns_none(self):
        mq = MessageQueue(10)
        assert mq.dequeue() is None

    def test_full_queue_rejects_message(self):
        mq = MessageQueue(1)
        mq.enqueue(FireStatusMessage(1, 1, True))
        assert not mq.enqueue(FireStatusMessage(2, 2, True))

    def test_is_empty(self):
        mq = MessageQueue(10)
        assert mq.is_empty()
        mq.enqueue(FireStatusMessage(1, 1, True))
        assert not mq.is_empty()


# ---------------------------------------------------------------------------
# RecalculationTrigger tests
# ---------------------------------------------------------------------------

class TestRecalculationTrigger:
    def test_fire_detection_priority(self):
        trigger = RecalculationTrigger(TriggerType.FIRE_DETECTION, [1])
        assert trigger.priority == 10

    def test_manual_trigger_is_full_recalculation(self):
        trigger = RecalculationTrigger(TriggerType.MANUAL, [])
        assert trigger.is_full_recalculation()

    def test_fire_detection_not_full_recalculation(self):
        trigger = RecalculationTrigger(TriggerType.FIRE_DETECTION, [1])
        assert not trigger.is_full_recalculation()

    def test_get_affected_exit_signs_full_recalc(self):
        graph = _make_graph()
        trigger = RecalculationTrigger(TriggerType.MANUAL, [])
        exits = trigger.get_affected_exit_signs(graph)
        # Vertices 3 and 4 are EXITs
        assert set(exits) == {3, 4}

    def test_get_affected_exit_signs_local(self):
        graph = _make_graph()
        # Affected vertex is 2 (INTERSECTION) which neighbours 3 and 4 (EXITs)
        trigger = RecalculationTrigger(TriggerType.FIRE_DETECTION, [2])
        exits = trigger.get_affected_exit_signs(graph)
        assert set(exits) == {3, 4}


# ---------------------------------------------------------------------------
# Full RouteProcessingThread integration tests
# ---------------------------------------------------------------------------

class TestRouteProcessingThread:
    """Integration tests that exercise the complete processing pipeline."""

    def _make_thread(self) -> RouteProcessingThread:
        """Build a thread with a graph that exercises the full pipeline.

        Linear corridor topology (single floor):

            v1 (ROOM, alarm 101) --10m--> v2 (EXIT, sign 201) --5m--> v3 (EXIT, sign 202) --3m--> v4 (EXIT)

        Routing FROM exit-sign vertices (v2, v3) TO the nearest EXIT:
          - v2 → nearest EXIT is v3  (5 m)  → valid route → RouteUpdateMessage
          - v3 → nearest EXIT is v4  (3 m)  → valid route → RouteUpdateMessage
          - v4 → no further EXIT reachable   → no route   → no message
        """
        config = _make_config()
        thread = RouteProcessingThread(config)
        graph = thread.graph
        v1 = Vertex(1, 0.0, 0.0, 0, VertexType.ROOM)
        v1.add_device(101)   # smoke alarm
        v2 = Vertex(2, 10.0, 0.0, 0, VertexType.EXIT)
        v2.add_device(201)   # exit sign (intermediate)
        v3 = Vertex(3, 15.0, 0.0, 0, VertexType.EXIT)
        v3.add_device(202)   # exit sign (intermediate)
        v4 = Vertex(4, 18.0, 0.0, 0, VertexType.EXIT)  # final exit door
        for v in (v1, v2, v3, v4):
            graph.add_vertex(v)
        graph.add_edge(Edge(1, 2, 10.0))
        graph.add_edge(Edge(2, 3, 5.0))
        graph.add_edge(Edge(3, 4, 3.0))
        return thread

    # -- basic lifecycle --------------------------------------------------------

    def test_thread_starts_and_stops(self):
        thread = self._make_thread()
        thread.start()
        assert thread.is_alive()
        thread.stop()
        thread.join(timeout=2.0)
        assert not thread.is_alive()

    # -- manual trigger ---------------------------------------------------------

    def test_manual_trigger_produces_route_updates(self):
        """A MANUAL_TRIGGER message must cause RouteUpdateMessages on the output queue."""
        from src.messaging.message import Message
        from src.messaging.message_type import MessageType

        class ManualTriggerMessage(Message):
            def __init__(self):
                super().__init__(MessageType.MANUAL_TRIGGER)

            def serialize(self) -> bytes:
                return b""

        thread = self._make_thread()
        thread.start()

        thread.input_queue.enqueue(ManualTriggerMessage())
        updates = _drain_output(thread, timeout=1.5)

        thread.stop()
        thread.join(timeout=2.0)

        assert len(updates) > 0, "Expected at least one RouteUpdateMessage after manual trigger"
        sign_ids = {u.exit_sign_id for u in updates}
        # v2 (sign 201) and v3 (sign 202) are intermediate EXIT sign vertices with
        # valid routes to the next EXIT; v4 is the final door and has no onward route.
        assert sign_ids == {2, 3}

    # -- fire status handling ---------------------------------------------------

    def test_fire_detection_triggers_recalculation(self):
        """FireStatusMessage with fire=True must mark the hazard and produce output."""
        thread = self._make_thread()
        thread.start()

        fire_msg = FireStatusMessage(101, 1, True, confidence=0.95)
        thread.input_queue.enqueue(fire_msg)
        updates = _drain_output(thread, timeout=1.5)

        thread.stop()
        thread.join(timeout=2.0)

        assert len(updates) > 0, "Expected route updates after fire detection"

    def test_fire_detection_marks_vertex_as_hazard(self):
        """After a fire message the relevant vertex must be flagged as a hazard."""
        thread = self._make_thread()
        thread.start()

        thread.input_queue.enqueue(FireStatusMessage(101, 1, True, confidence=0.9))
        time.sleep(0.3)

        thread.stop()
        thread.join(timeout=2.0)

        vertex = thread.graph.get_vertex(1)
        assert vertex.is_hazard

    def test_fire_cleared_removes_hazard(self):
        """A fire=False message should clear the hazard."""
        thread = self._make_thread()
        thread.start()

        thread.input_queue.enqueue(FireStatusMessage(101, 1, True, confidence=0.9))
        time.sleep(0.2)
        thread.input_queue.enqueue(FireStatusMessage(101, 1, False))
        time.sleep(0.3)

        thread.stop()
        thread.join(timeout=2.0)

        vertex = thread.graph.get_vertex(1)
        assert not vertex.is_hazard

    # -- device down handling --------------------------------------------------

    def test_device_down_recorded_in_tracker(self):
        """A DeviceDownMessage must register the device as OFFLINE in the tracker."""
        thread = self._make_thread()
        thread.start()

        thread.input_queue.enqueue(
            DeviceDownMessage(201, DeviceType.EXIT_SIGN, 2)
        )
        time.sleep(0.3)

        thread.stop()
        thread.join(timeout=2.0)

        status = thread._device_tracker.get_device_status(201)
        assert status is not None
        assert status.is_failed()

    def test_device_down_triggers_recalculation(self):
        """A DeviceDownMessage must cause at least one RouteUpdateMessage to be emitted."""
        thread = self._make_thread()
        thread.start()

        # Device down for exit sign at vertex 2; route from v2 to nearest EXIT (v3) is valid.
        thread.input_queue.enqueue(
            DeviceDownMessage(201, DeviceType.EXIT_SIGN, 2)
        )
        updates = _drain_output(thread, timeout=1.5)

        thread.stop()
        thread.join(timeout=2.0)

        assert len(updates) > 0, "Expected route updates after device-down event"

    # -- output message content ------------------------------------------------

    def test_route_update_message_fields(self):
        """RouteUpdateMessage objects emitted by the thread must have sensible field values."""
        from src.messaging.message import Message
        from src.messaging.message_type import MessageType

        class ManualTriggerMessage(Message):
            def __init__(self):
                super().__init__(MessageType.MANUAL_TRIGGER)

            def serialize(self) -> bytes:
                return b""

        thread = self._make_thread()
        thread.start()

        thread.input_queue.enqueue(ManualTriggerMessage())
        updates = _drain_output(thread, timeout=1.5)

        thread.stop()
        thread.join(timeout=2.0)

        for upd in updates:
            assert upd.confidence_score >= 0.0
            assert upd.confidence_score <= 1.0
            assert upd.distance_to_next >= 0.0
            assert upd.direction is not None
            assert upd.urgency is not None

    # -- route caching ---------------------------------------------------------

    def test_cache_populated_after_recalculation(self):
        """After a recalculation the route cache should hold entries for EXIT vertices."""
        thread = self._make_thread()
        thread.start()

        from src.messaging.message import Message
        from src.messaging.message_type import MessageType

        class ManualTriggerMessage(Message):
            def __init__(self):
                super().__init__(MessageType.MANUAL_TRIGGER)

            def serialize(self) -> bytes:
                return b""

        thread.input_queue.enqueue(ManualTriggerMessage())
        time.sleep(0.5)

        thread.stop()
        thread.join(timeout=2.0)

        assert thread._route_cache.get_size() > 0

    # -- hazard spread integration ---------------------------------------------

    def test_hazard_spread_degrades_nearby_edges(self):
        """After a fire and a spread update the edges near the hazard must have
        reduced safety scores."""
        graph = _make_graph()
        manager = HazardManager(graph)
        manager.add_hazard(101, 1, 1.0)
        manager.update_hazard_spread()
        manager.apply_hazard_weights()

        edge_1_2 = graph.get_edge(1, 2)
        assert edge_1_2.safety_score < 100.0


# ---------------------------------------------------------------------------
# YamlGraphBuilder tests
# ---------------------------------------------------------------------------

#: Minimal DSL dict that mirrors the format produced by FloorPlanEditor.
_SAMPLE_DSL: dict = {
    "units": "meters",
    "junctions": [
        {"id": "J1", "position": [10.0, 20.0]},
        {"id": "J2", "position": [30.0, 20.0]},
    ],
    "terminals": [
        {"id": "T1", "position": [50.0, 20.0]},
    ],
    "corridors": [
        {"id": "C1", "from": "J1", "to": "J2", "length": 20.0},
        {"id": "C2", "from": "J2", "to": "T1", "length": 20.0},
    ],
    "rooms": [
        {"id": "R1", "attached_to": "J1", "door_cost": 2.0},
        {"id": "R2", "attached_to": None, "door_cost": 1.5},
    ],
    "room_connections": [
        {"from": "R1", "to": "R2", "cost": 10.0},
    ],
    "fire_exits": [
        {"id": "FE1", "attached_to": "T1"},
        {"id": "FE2", "attached_to": "J2"},
    ],
}


class TestYamlGraphBuilder:
    """Unit tests for YamlGraphBuilder – DSL YAML → BuildingGraph conversion."""

    def _build(self) -> tuple:
        builder = YamlGraphBuilder()
        graph = builder.build_from_dict(_SAMPLE_DSL)
        return builder, graph

    # -- vertex types ----------------------------------------------------------

    def test_junctions_become_intersection_vertices(self):
        _, graph = self._build()
        # J1 and J2 must exist as INTERSECTION
        junction_types = {
            v.type for v in graph.get_all_vertices()
            if v.type == VertexType.INTERSECTION
        }
        assert VertexType.INTERSECTION in junction_types

    def test_terminals_become_exit_vertices(self):
        _, graph = self._build()
        exit_types = {
            v.type for v in graph.get_all_vertices()
            if v.type == VertexType.EXIT
        }
        assert VertexType.EXIT in exit_types

    def test_rooms_become_room_vertices(self):
        _, graph = self._build()
        room_types = {
            v.type for v in graph.get_all_vertices()
            if v.type == VertexType.ROOM
        }
        assert VertexType.ROOM in room_types

    def test_correct_vertex_count(self):
        # junctions(2) + terminals(1) + rooms(2) = 5 vertices
        _, graph = self._build()
        assert graph.get_vertex_count() == 5

    # -- vertex positions ------------------------------------------------------

    def test_junction_position_preserved(self):
        builder, graph = self._build()
        j1_vid = builder.get_vertex_id("J1")
        v = graph.get_vertex(j1_vid)
        assert v is not None
        assert v.x == pytest.approx(10.0)
        assert v.y == pytest.approx(20.0)

    def test_terminal_position_preserved(self):
        builder, graph = self._build()
        t1_vid = builder.get_vertex_id("T1")
        v = graph.get_vertex(t1_vid)
        assert v is not None
        assert v.x == pytest.approx(50.0)
        assert v.y == pytest.approx(20.0)

    # -- corridor edges --------------------------------------------------------

    def test_corridors_create_bidirectional_edges(self):
        builder, graph = self._build()
        j1 = builder.get_vertex_id("J1")
        j2 = builder.get_vertex_id("J2")
        assert graph.get_edge(j1, j2) is not None
        assert graph.get_edge(j2, j1) is not None

    def test_corridor_edge_distance(self):
        builder, graph = self._build()
        j1 = builder.get_vertex_id("J1")
        j2 = builder.get_vertex_id("J2")
        edge = graph.get_edge(j1, j2)
        assert edge.base_distance == pytest.approx(20.0)

    # -- portal links (room attached_to junction) ------------------------------

    def test_attached_room_has_portal_edges(self):
        builder, graph = self._build()
        r1 = builder.get_vertex_id("R1")
        j1 = builder.get_vertex_id("J1")
        assert graph.get_edge(r1, j1) is not None
        assert graph.get_edge(j1, r1) is not None

    def test_portal_edge_uses_door_cost(self):
        builder, graph = self._build()
        r1 = builder.get_vertex_id("R1")
        j1 = builder.get_vertex_id("J1")
        assert graph.get_edge(r1, j1).base_distance == pytest.approx(2.0)

    def test_unattached_room_has_no_portal_edges(self):
        builder, graph = self._build()
        r2 = builder.get_vertex_id("R2")
        j1 = builder.get_vertex_id("J1")
        # R2 has attached_to=None so no portal edge should exist to J1
        assert graph.get_edge(r2, j1) is None

    # -- room-to-room connections ----------------------------------------------

    def test_room_connection_creates_bidirectional_edges(self):
        builder, graph = self._build()
        r1 = builder.get_vertex_id("R1")
        r2 = builder.get_vertex_id("R2")
        assert graph.get_edge(r1, r2) is not None
        assert graph.get_edge(r2, r1) is not None

    def test_room_connection_cost(self):
        builder, graph = self._build()
        r1 = builder.get_vertex_id("R1")
        r2 = builder.get_vertex_id("R2")
        assert graph.get_edge(r1, r2).base_distance == pytest.approx(10.0)

    # -- fire-exit signs -------------------------------------------------------

    def test_fire_exits_attached_as_devices(self):
        builder, graph = self._build()
        t1_vid = builder.get_vertex_id("T1")
        fe1_id = builder.get_vertex_id("FE1")
        vertex = graph.get_vertex(t1_vid)
        assert fe1_id in vertex.get_device_ids()

    def test_fire_exit_on_junction(self):
        builder, graph = self._build()
        j2_vid = builder.get_vertex_id("J2")
        fe2_id = builder.get_vertex_id("FE2")
        vertex = graph.get_vertex(j2_vid)
        assert fe2_id in vertex.get_device_ids()

    # -- get_vertex_id ---------------------------------------------------------

    def test_unknown_label_returns_none(self):
        builder, _ = self._build()
        assert builder.get_vertex_id("UNKNOWN_999") is None

    def test_known_labels_return_integers(self):
        builder, _ = self._build()
        for label in ("J1", "J2", "T1", "R1", "R2"):
            vid = builder.get_vertex_id(label)
            assert isinstance(vid, int)

    # -- RouteProcessingThread integration ------------------------------------

    def test_load_graph_from_yaml_populates_thread_graph(self, tmp_path):
        """load_graph_from_yaml() must replace the thread graph with one built
        from the DSL YAML and wire up the route calculator correctly."""
        yaml_file = tmp_path / "test_floor.yaml"
        yaml_file.write_text(yaml.dump(_SAMPLE_DSL))

        thread = RouteProcessingThread(_make_config())
        assert thread.graph.get_vertex_count() == 0  # empty before loading

        builder = thread.load_graph_from_yaml(str(yaml_file))

        assert thread.graph.get_vertex_count() == 5
        assert builder.get_vertex_id("T1") is not None

    def test_load_graph_route_calculator_uses_new_graph(self, tmp_path):
        """After load_graph_from_yaml() the route calculator must find EXIT
        vertices from the loaded floor plan."""
        yaml_file = tmp_path / "floor.yaml"
        yaml_file.write_text(yaml.dump(_SAMPLE_DSL))

        thread = RouteProcessingThread(_make_config())
        builder = thread.load_graph_from_yaml(str(yaml_file))

        j1_vid = builder.get_vertex_id("J1")
        route = thread._route_calculator.calculate_route(j1_vid, VertexType.EXIT)
        # J1 → J2 → T1 (EXIT) should be reachable
        assert route is not None
        assert route.is_valid()

