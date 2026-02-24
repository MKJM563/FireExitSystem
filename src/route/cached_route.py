from datetime import datetime, timedelta

from src.route.route import Route


class CachedRoute:
    def __init__(self, route: Route, timestamp: datetime) -> None:
        self._route: Route = route
        self._timestamp: datetime = timestamp
        self._access_count: int = 0

    @property
    def route(self) -> Route:
        return self._route

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def access_count(self) -> int:
        return self._access_count

    def is_valid(self, current_time: datetime, max_age: timedelta) -> bool:
        return (current_time - self._timestamp) <= max_age

    def increment_access(self) -> None:
        self._access_count += 1

    def __repr__(self) -> str:
        return f"CachedRoute(route={self._route}, timestamp={self._timestamp}, accesses={self._access_count})"
