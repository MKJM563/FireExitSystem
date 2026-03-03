from __future__ import annotations
import threading
import time
from datetime import timedelta
from typing import Dict, List, Optional

from src.graph.building_graph import BuildingGraph
from src.graph.vertex_type import VertexType
from src.graph.yaml_graph_builder import YamlGraphBuilder
from src.graph.graph_cache import GraphCache
from src.route.route_calculator import RouteCalculator
from src.route.route_cache import RouteCache
from src.route.route import Route
from src.route.direction import Direction
from src.route.urgency_level import UrgencyLevel
from src.hazard.hazard_manager import HazardManager
from src.hazard.device_status_tracker import DeviceStatusTracker
from src.hazard.device_status import DeviceStatus
from src.hazard.operational_status import OperationalStatus
from src.hazard.device_type import DeviceType
from src.messaging.message_queue import MessageQueue
from src.messaging.fire_status_message import FireStatusMessage
from src.messaging.device_down_message import DeviceDownMessage
from src.messaging.route_update_message import RouteUpdateMessage
from src.thread.configuration import Configuration
from src.thread.recalculation_trigger import RecalculationTrigger
from src.thread.scheduler import Scheduler
from src.thread.trigger_type import TriggerType


class RouteProcessingThread(threading.Thread):
    def __init__(
        self,
        config: Configuration,
        cache_dir: Optional[str] = None,
        auto_save_interval_seconds: float = 30.0,
    ) -> None:
        super().__init__(daemon=True)
        self._configuration: Configuration = config
        self._graph: BuildingGraph = BuildingGraph()
        self._route_calculator: RouteCalculator = RouteCalculator(self._graph, config)
        self._hazard_manager: HazardManager = HazardManager(self._graph)
        self._device_tracker: DeviceStatusTracker = DeviceStatusTracker()
        self._route_cache: RouteCache = RouteCache(config.cache_size)
        self._input_queue: MessageQueue = MessageQueue(max_size=1000)
        self._output_queue: MessageQueue = MessageQueue(max_size=1000)
        self._is_running: bool = False
        self._recalculation_scheduler: Scheduler = Scheduler()
        self._last_recalc_time: float = 0.0
        self._debounce_seconds: float = config.recalculation_debounce_ms / 1000.0
        self._graph_cache: GraphCache = GraphCache(cache_dir)
        self._yaml_path: Optional[str] = None
        self._builder_id_map: Dict[str, int] = {}
        self._auto_save_interval: float = auto_save_interval_seconds
        self._last_auto_save: float = 0.0

    @property
    def graph(self) -> BuildingGraph:
        return self._graph

    @property
    def graph_cache(self) -> GraphCache:
        """Return the GraphCache instance for cache management."""
        return self._graph_cache

    def load_graph_from_yaml(
        self,
        yaml_path: str,
        use_cache: bool = True,
        restore_runtime_state: bool = False,
    ) -> YamlGraphBuilder:
        """Populate the internal graph from a floor-plan DSL YAML file.

        The YAML must follow the format produced by
        :class:`~fire_evacuation_system.floor_plan_editor.FloorPlanEditor`.

        Args:
            yaml_path: Path to the YAML floor-plan file.
            use_cache: If True, attempt to load from disk cache first.
                      Set to False to force re-parsing the YAML.
            restore_runtime_state: If True, attempt to restore the last saved
                      runtime state (with all modifications). Falls back to
                      initial cache or YAML parsing if no runtime state exists.

        Returns:
            The :class:`~src.graph.yaml_graph_builder.YamlGraphBuilder`
            used for the conversion so callers can inspect the string-to-integer
            vertex-ID mapping.
        """
        self._yaml_path = yaml_path
        builder = YamlGraphBuilder()
        cache = self._graph_cache if use_cache else None
        self._graph = builder.build_from_file(
            yaml_path,
            cache=cache,
            restore_runtime_state=restore_runtime_state,
        )
        self._builder_id_map = builder.id_map.copy()
        self._route_calculator = RouteCalculator(self._graph, self._configuration)
        self._hazard_manager = HazardManager(self._graph)
        return builder

    def save_runtime_state(self) -> bool:
        """Save the current graph state including all runtime modifications.

        This persists safety scores, hazard markers, edge status, and other
        runtime changes so they can be restored after a restart.

        Returns:
            True if saved successfully, False if no YAML path is set.
        """
        if self._yaml_path is None:
            return False
        self._graph_cache.save_runtime_state(
            self._yaml_path,
            self._graph,
            self._builder_id_map,
        )
        self._last_auto_save = time.monotonic()
        return True

    def _maybe_auto_save(self) -> None:
        """Auto-save runtime state if interval has elapsed and there are changes."""
        if self._yaml_path is None:
            return
        if not self._graph_cache.is_dirty:
            return
        if time.monotonic() - self._last_auto_save >= self._auto_save_interval:
            self.save_runtime_state()

    @property
    def input_queue(self) -> MessageQueue:
        return self._input_queue

    @property
    def output_queue(self) -> MessageQueue:
        return self._output_queue

    def start(self) -> None:
        # Schedule periodic hazard spread updates before starting the thread
        self._recalculation_scheduler.schedule_repeating(
            self._periodic_recalculation,
            timedelta(seconds=self._configuration.spread_interval_seconds),
        )
        self._is_running = True
        super().start()

    def stop(self, save_state: bool = True) -> None:
        """Stop the processing thread.

        Args:
            save_state: If True, save the current runtime state before stopping.
        """
        self._is_running = False
        if save_state:
            self.save_runtime_state()

    def run(self) -> None:
        while self._is_running:
            self._process_messages()
            self._recalculation_scheduler.execute_ready_tasks()
            self._maybe_auto_save()
            time.sleep(0.01)  # 10ms sleep to avoid busy-waiting

    def _process_messages(self) -> None:
        # Process up to 50 messages per loop iteration
        for _ in range(50):
            msg = self._input_queue.dequeue()
            if msg is None:
                break
            from src.messaging.message_type import MessageType
            if msg.get_type() == MessageType.FIRE_STATUS:
                self._handle_fire_status(msg)  # type: ignore[arg-type]
            elif msg.get_type() == MessageType.DEVICE_DOWN:
                self._handle_device_down(msg)  # type: ignore[arg-type]
            elif msg.get_type() == MessageType.MANUAL_TRIGGER:
                self._handle_manual_trigger()

    def _handle_fire_status(self, msg: FireStatusMessage) -> None:
        if msg.fire_detected:
            self._hazard_manager.add_hazard(msg.device_id, msg.vertex_id, msg.confidence)
            self._graph_cache.mark_dirty()  # Graph state changed
            trigger = RecalculationTrigger(TriggerType.FIRE_DETECTION, [msg.vertex_id])
            if self._should_recalculate(trigger):
                self._perform_route_recalculation(trigger)
        else:
            self._hazard_manager.remove_hazard(msg.device_id)
            self._graph_cache.mark_dirty()  # Graph state changed

    def _handle_device_down(self, msg: DeviceDownMessage) -> None:
        status = DeviceStatus(msg.device_id, msg.device_type, OperationalStatus.OFFLINE)
        status.vertex_id = msg.vertex_id
        self._device_tracker.update_device_status(msg.device_id, status)
        trigger = RecalculationTrigger(TriggerType.DEVICE_FAILURE, [msg.vertex_id])
        if self._should_recalculate(trigger):
            self._perform_route_recalculation(trigger)

    def _handle_manual_trigger(self) -> None:
        trigger = RecalculationTrigger(TriggerType.MANUAL, [])
        self._perform_route_recalculation(trigger)

    def _periodic_recalculation(self) -> None:
        affected = self._hazard_manager.update_hazard_spread()
        self._hazard_manager.apply_hazard_weights()
        if affected:
            self._graph_cache.mark_dirty()  # Edge weights/hazards changed
        trigger_type = TriggerType.HAZARD_SPREAD if affected else TriggerType.PERIODIC
        trigger = RecalculationTrigger(trigger_type, affected)
        self._perform_route_recalculation(trigger)

    def _perform_route_recalculation(self, trigger: RecalculationTrigger) -> None:
        exit_sign_vertices = trigger.get_affected_exit_signs(self._graph)
        if not exit_sign_vertices:
            # Fall back to all exit vertices
            exit_sign_vertices = [
                v.id for v in self._graph.get_all_vertices()
                if v.type == VertexType.EXIT
            ]
        routes: Dict[int, Route] = {}
        for vertex_id in exit_sign_vertices:
            # Check cache first
            cached = self._route_cache.get(vertex_id, VertexType.EXIT, self._configuration.routing_mode)
            if cached is not None:
                routes[vertex_id] = cached
            else:
                route = self._route_calculator.calculate_route(vertex_id, VertexType.EXIT)
                if route is not None:
                    self._route_cache.put(vertex_id, VertexType.EXIT, self._configuration.routing_mode, route)
                    routes[vertex_id] = route

        update_messages = self._generate_route_update_messages(routes)
        self._send_to_device_data_processing(update_messages)
        self._last_recalc_time = time.monotonic()

    def _generate_route_update_messages(self, routes: Dict[int, Route]) -> List[RouteUpdateMessage]:
        messages: List[RouteUpdateMessage] = []
        for sign_id, route in routes.items():
            if not route.is_valid():
                continue
            direction = route.get_direction(sign_id, 0.0)
            distance = route.get_distance_to_next(sign_id)
            msg = RouteUpdateMessage(sign_id, direction, distance)
            msg.confidence_score = route.get_confidence_score()
            msg.urgency = route.urgency
            messages.append(msg)
        return messages

    def _send_to_device_data_processing(self, messages: List[RouteUpdateMessage]) -> None:
        for msg in messages:
            self._output_queue.enqueue(msg)

    def _should_recalculate(self, trigger: RecalculationTrigger) -> bool:
        now = time.monotonic()
        if trigger.priority >= 8:
            return True
        return (now - self._last_recalc_time) >= self._debounce_seconds
