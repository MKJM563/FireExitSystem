from __future__ import annotations
import json
import os
from typing import TYPE_CHECKING

from src.route.weight_factors import WeightFactors
from src.route.routing_mode import RoutingMode

if TYPE_CHECKING:
    pass


class Configuration:
    def __init__(self) -> None:
        self._graph_definition_file: str = "graph.json"
        self._weight_factors: WeightFactors = WeightFactors.get_preset(RoutingMode.SAFETY_FIRST)
        self._routing_mode: RoutingMode = RoutingMode.SAFETY_FIRST
        self._hazard_propagation_radius: int = 3
        self._spread_interval_seconds: int = 30
        self._cache_size: int = 100
        self._recalculation_debounce_ms: int = 500

    @property
    def graph_definition_file(self) -> str:
        return self._graph_definition_file

    @property
    def weight_factors(self) -> WeightFactors:
        return self._weight_factors

    @property
    def routing_mode(self) -> RoutingMode:
        return self._routing_mode

    @property
    def hazard_propagation_radius(self) -> int:
        return self._hazard_propagation_radius

    @property
    def spread_interval_seconds(self) -> int:
        return self._spread_interval_seconds

    @property
    def cache_size(self) -> int:
        return self._cache_size

    @property
    def recalculation_debounce_ms(self) -> int:
        return self._recalculation_debounce_ms

    @staticmethod
    def load_from_file(path: str) -> "Configuration":
        config = Configuration()
        if not os.path.exists(path):
            return config
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        config._graph_definition_file = data.get("graph_definition_file", config._graph_definition_file)
        config._hazard_propagation_radius = data.get("hazard_propagation_radius", config._hazard_propagation_radius)
        config._spread_interval_seconds = data.get("spread_interval_seconds", config._spread_interval_seconds)
        config._cache_size = data.get("cache_size", config._cache_size)
        config._recalculation_debounce_ms = data.get("recalculation_debounce_ms", config._recalculation_debounce_ms)
        mode_str = data.get("routing_mode", config._routing_mode.value)
        config._routing_mode = RoutingMode(mode_str)
        wf = data.get("weight_factors")
        if wf:
            config._weight_factors = WeightFactors(
                wf.get("distance", 0.2),
                wf.get("safety", 0.7),
                wf.get("congestion", 0.1),
            )
        else:
            config._weight_factors = WeightFactors.get_preset(config._routing_mode)
        return config

    def validate(self) -> bool:
        return (
            self._hazard_propagation_radius > 0
            and self._spread_interval_seconds > 0
            and self._cache_size > 0
            and self._recalculation_debounce_ms >= 0
            and self._weight_factors.validate()
        )

    def save_to_file(self, path: str) -> None:
        data = {
            "graph_definition_file": self._graph_definition_file,
            "routing_mode": self._routing_mode.value,
            "hazard_propagation_radius": self._hazard_propagation_radius,
            "spread_interval_seconds": self._spread_interval_seconds,
            "cache_size": self._cache_size,
            "recalculation_debounce_ms": self._recalculation_debounce_ms,
            "weight_factors": {
                "distance": self._weight_factors.distance_weight,
                "safety": self._weight_factors.safety_weight,
                "congestion": self._weight_factors.congestion_weight,
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
