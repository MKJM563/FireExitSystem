from __future__ import annotations
from src.route.routing_mode import RoutingMode


class WeightFactors:
    def __init__(self, dist: float, safety: float, congestion: float) -> None:
        self._distance_weight: float = dist
        self._safety_weight: float = safety
        self._congestion_weight: float = congestion

    @property
    def distance_weight(self) -> float:
        return self._distance_weight

    @property
    def safety_weight(self) -> float:
        return self._safety_weight

    @property
    def congestion_weight(self) -> float:
        return self._congestion_weight

    @staticmethod
    def get_preset(mode: RoutingMode) -> "WeightFactors":
        if mode == RoutingMode.SAFETY_FIRST:
            return WeightFactors(dist=0.2, safety=0.7, congestion=0.1)
        elif mode == RoutingMode.SPEED:
            return WeightFactors(dist=0.7, safety=0.1, congestion=0.2)
        elif mode == RoutingMode.ACCESSIBILITY:
            return WeightFactors(dist=0.3, safety=0.4, congestion=0.3)
        return WeightFactors(dist=0.33, safety=0.34, congestion=0.33)

    def validate(self) -> bool:
        total = self._distance_weight + self._safety_weight + self._congestion_weight
        return (
            abs(total - 1.0) < 1e-6
            and self._distance_weight >= 0
            and self._safety_weight >= 0
            and self._congestion_weight >= 0
        )

    def __repr__(self) -> str:
        return (
            f"WeightFactors(dist={self._distance_weight}, "
            f"safety={self._safety_weight}, congestion={self._congestion_weight})"
        )
