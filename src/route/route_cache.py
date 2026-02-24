from __future__ import annotations
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

from src.graph.vertex_type import VertexType
from src.route.routing_mode import RoutingMode
from src.route.route import Route
from src.route.route_cache_key import RouteCacheKey
from src.route.cached_route import CachedRoute

_MAX_AGE = timedelta(minutes=5)


class RouteCache:
    def __init__(self, max_size: int) -> None:
        self._max_size: int = max_size
        self._cache: OrderedDict[RouteCacheKey, CachedRoute] = OrderedDict()

    def get(self, start_id: int, target_type: VertexType, routing_mode: RoutingMode) -> Optional[Route]:
        key = RouteCacheKey(start_id, target_type, routing_mode)
        cached = self._cache.get(key)
        if cached is None:
            return None
        if not cached.is_valid(datetime.now(), _MAX_AGE):
            del self._cache[key]
            return None
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        cached.increment_access()
        return cached.route

    def put(self, start_id: int, target_type: VertexType, routing_mode: RoutingMode, route: Route) -> None:
        key = RouteCacheKey(start_id, target_type, routing_mode)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = CachedRoute(route, datetime.now())
        if len(self._cache) > self._max_size:
            self._evict_lru()

    def invalidate(self, vertex_id: int, radius: int) -> None:
        """Remove all cache entries whose start vertex matches vertex_id (simple approximation)."""
        keys_to_remove = [k for k in self._cache if k.start_vertex_id == vertex_id]
        for key in keys_to_remove:
            del self._cache[key]

    def invalidate_all(self) -> None:
        self._cache.clear()

    def get_size(self) -> int:
        return len(self._cache)

    def _evict_lru(self) -> None:
        # OrderedDict: first item is least recently used
        if self._cache:
            self._cache.popitem(last=False)
