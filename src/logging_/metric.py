import math
from typing import List


class Metric:
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._count: int = 0
        self._sum: float = 0.0
        self._min: float = float("inf")
        self._max: float = float("-inf")
        self._values: List[float] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def count(self) -> int:
        return self._count

    def record(self, value: float) -> None:
        self._count += 1
        self._sum += value
        self._values.append(value)
        if value < self._min:
            self._min = value
        if value > self._max:
            self._max = value

    def get_average(self) -> float:
        if self._count == 0:
            return 0.0
        return self._sum / self._count

    def get_90th_percentile(self) -> float:
        if not self._values:
            return 0.0
        sorted_values = sorted(self._values)
        idx = math.ceil(0.9 * len(sorted_values)) - 1
        return sorted_values[max(0, idx)]

    def __repr__(self) -> str:
        return (
            f"Metric(name={self._name}, count={self._count}, "
            f"avg={self.get_average():.3f}, min={self._min}, max={self._max})"
        )
