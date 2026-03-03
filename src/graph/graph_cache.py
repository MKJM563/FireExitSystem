"""Persistent disk cache for :class:`BuildingGraph` instances.

This module provides two types of caching:

1. **Initial state cache**: Speeds up YAML parsing by caching the freshly-built
   graph. Automatically invalidated when the source YAML changes.

2. **Runtime state cache**: Persists the current graph state including all
   runtime modifications (safety scores, hazards, edge status, etc.). This
   allows the system to restore its state after a restart.
"""
from __future__ import annotations

import hashlib
import os
import pickle
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from src.graph.building_graph import BuildingGraph


@dataclass
class CachedGraphData:
    """Container for cached graph and associated metadata."""

    graph: BuildingGraph
    id_map: Dict[str, int]
    source_hash: str
    source_mtime: float


@dataclass
class RuntimeStateData:
    """Container for runtime graph state with modification tracking."""

    graph: BuildingGraph
    id_map: Dict[str, int]
    source_yaml_path: str
    source_hash: str
    last_modified: datetime = field(default_factory=datetime.now)
    modification_count: int = 0


class GraphCache:
    """Manages persistent disk caching of :class:`BuildingGraph` instances.

    Supports two caching modes:

    **Initial State Cache** (for fast startup):
    - Caches the graph as parsed from YAML
    - Automatically invalidated when YAML file changes
    - Use: ``load()`` and ``save()``

    **Runtime State Cache** (for persistence across restarts):
    - Caches the current graph state including all runtime modifications
    - Preserves safety scores, hazard markers, edge status, etc.
    - Use: ``load_runtime_state()`` and ``save_runtime_state()``

    Usage::

        cache = GraphCache()

        # Load with runtime state restoration (falls back to YAML if no state)
        graph, id_map = cache.load_with_fallback("floor_plan.yaml", builder)

        # ... runtime modifications happen ...

        # Save current state periodically or on shutdown
        cache.save_runtime_state("floor_plan.yaml", graph, id_map)
    """

    DEFAULT_CACHE_DIR = ".graph_cache"
    CACHE_VERSION = 1

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """Initialize the cache.

        Args:
            cache_dir: Directory for cache files. Defaults to `.graph_cache`
                      in the current working directory.
        """
        self._cache_dir = Path(cache_dir) if cache_dir else Path(self.DEFAULT_CACHE_DIR)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._dirty = False  # Track if runtime state has unsaved changes

    def _get_cache_path(self, yaml_path: str, runtime: bool = False) -> Path:
        """Generate cache file path based on the YAML file path."""
        path_hash = hashlib.md5(os.path.abspath(yaml_path).encode()).hexdigest()[:12]
        filename = Path(yaml_path).stem
        suffix = ".runtime.cache" if runtime else ".cache"
        return self._cache_dir / f"{filename}_{path_hash}{suffix}"

    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file contents."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_file_mtime(self, file_path: str) -> float:
        """Get modification time of a file."""
        return os.path.getmtime(file_path)

    # =========================================================================
    # Initial State Cache (YAML parsing optimization)
    # =========================================================================

    def is_cache_valid(self, yaml_path: str) -> bool:
        """Check if a valid initial-state cache exists for the given YAML file."""
        cache_path = self._get_cache_path(yaml_path)
        if not cache_path.exists():
            return False

        try:
            with open(cache_path, "rb") as f:
                cached_data: CachedGraphData = pickle.load(f)

            current_mtime = self._get_file_mtime(yaml_path)
            if current_mtime != cached_data.source_mtime:
                current_hash = self._compute_file_hash(yaml_path)
                if current_hash != cached_data.source_hash:
                    return False

            return True
        except (pickle.UnpicklingError, AttributeError, EOFError, KeyError):
            return False

    def load(self, yaml_path: str) -> Optional[Tuple[BuildingGraph, Dict[str, int]]]:
        """Load a cached initial-state graph if available and valid."""
        if not self.is_cache_valid(yaml_path):
            return None

        cache_path = self._get_cache_path(yaml_path)
        try:
            with open(cache_path, "rb") as f:
                cached_data: CachedGraphData = pickle.load(f)
            return cached_data.graph, cached_data.id_map
        except (pickle.UnpicklingError, AttributeError, EOFError):
            self.invalidate(yaml_path)
            return None

    def save(
        self,
        yaml_path: str,
        graph: BuildingGraph,
        id_map: Dict[str, int],
    ) -> None:
        """Save the initial graph state to cache."""
        cache_path = self._get_cache_path(yaml_path)

        cached_data = CachedGraphData(
            graph=graph,
            id_map=id_map,
            source_hash=self._compute_file_hash(yaml_path),
            source_mtime=self._get_file_mtime(yaml_path),
        )

        with self._lock:
            with open(cache_path, "wb") as f:
                pickle.dump(cached_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def invalidate(self, yaml_path: str) -> bool:
        """Remove cached initial-state data for a YAML file."""
        cache_path = self._get_cache_path(yaml_path)
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    # =========================================================================
    # Runtime State Cache (preserves modifications)
    # =========================================================================

    def has_runtime_state(self, yaml_path: str) -> bool:
        """Check if a runtime state cache exists for the given YAML file.

        Note: This does NOT validate against YAML changes - runtime state
        is considered valid even if YAML has changed (user may want to
        preserve runtime modifications).
        """
        cache_path = self._get_cache_path(yaml_path, runtime=True)
        return cache_path.exists()

    def is_runtime_state_compatible(self, yaml_path: str) -> bool:
        """Check if runtime state cache was built from the same YAML version.

        Returns True if runtime state exists AND was built from the current
        YAML file (same hash). Returns False if YAML has changed since the
        runtime state was saved.
        """
        cache_path = self._get_cache_path(yaml_path, runtime=True)
        if not cache_path.exists():
            return False

        try:
            with open(cache_path, "rb") as f:
                runtime_data: RuntimeStateData = pickle.load(f)
            current_hash = self._compute_file_hash(yaml_path)
            return runtime_data.source_hash == current_hash
        except (pickle.UnpicklingError, AttributeError, EOFError):
            return False

    def load_runtime_state(
        self, yaml_path: str
    ) -> Optional[Tuple[BuildingGraph, Dict[str, int]]]:
        """Load the runtime state cache if available.

        Returns the graph with all runtime modifications (safety scores,
        hazards, edge status, etc.) preserved.

        Args:
            yaml_path: Path to the source YAML file.

        Returns:
            Tuple of (BuildingGraph, id_map) if runtime state exists,
            None otherwise.
        """
        cache_path = self._get_cache_path(yaml_path, runtime=True)
        if not cache_path.exists():
            return None

        try:
            with self._lock:
                with open(cache_path, "rb") as f:
                    runtime_data: RuntimeStateData = pickle.load(f)
            self._dirty = False
            return runtime_data.graph, runtime_data.id_map
        except (pickle.UnpicklingError, AttributeError, EOFError):
            self.invalidate_runtime_state(yaml_path)
            return None

    def save_runtime_state(
        self,
        yaml_path: str,
        graph: BuildingGraph,
        id_map: Dict[str, int],
    ) -> None:
        """Save the current graph state including all runtime modifications.

        This preserves:
        - Vertex hazard markers and confidence scores
        - Edge safety scores, congestion factors, and status
        - All accessibility flags

        Args:
            yaml_path: Path to the original YAML file.
            graph: The current BuildingGraph with modifications.
            id_map: Mapping from string labels to integer vertex IDs.
        """
        cache_path = self._get_cache_path(yaml_path, runtime=True)

        runtime_data = RuntimeStateData(
            graph=graph,
            id_map=id_map,
            source_yaml_path=yaml_path,
            source_hash=self._compute_file_hash(yaml_path),
            last_modified=datetime.now(),
        )

        with self._lock:
            with open(cache_path, "wb") as f:
                pickle.dump(runtime_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            self._dirty = False

    def invalidate_runtime_state(self, yaml_path: str) -> bool:
        """Remove runtime state cache for a YAML file."""
        cache_path = self._get_cache_path(yaml_path, runtime=True)
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    def mark_dirty(self) -> None:
        """Mark that the graph has unsaved runtime changes."""
        self._dirty = True

    @property
    def is_dirty(self) -> bool:
        """Return True if there are unsaved runtime changes."""
        return self._dirty

    # =========================================================================
    # Convenience methods
    # =========================================================================

    def load_with_runtime_fallback(
        self, yaml_path: str
    ) -> Optional[Tuple[BuildingGraph, Dict[str, int], bool]]:
        """Try to load runtime state first, fall back to initial state cache.

        Returns:
            Tuple of (graph, id_map, is_runtime_state) or None if no cache.
            The boolean indicates whether runtime state was loaded.
        """
        # Try runtime state first
        result = self.load_runtime_state(yaml_path)
        if result is not None:
            return result[0], result[1], True

        # Fall back to initial state cache
        result = self.load(yaml_path)
        if result is not None:
            return result[0], result[1], False

        return None

    def clear_all(self) -> int:
        """Remove all cached graphs (both initial and runtime states)."""
        count = 0
        for cache_file in self._cache_dir.glob("*.cache"):
            cache_file.unlink()
            count += 1
        return count

    def get_cache_info(self, yaml_path: str) -> Optional[Dict]:
        """Get information about cached data for a YAML file."""
        info = {}

        # Initial state cache info
        cache_path = self._get_cache_path(yaml_path)
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    cached_data: CachedGraphData = pickle.load(f)
                info["initial_state"] = {
                    "cache_path": str(cache_path),
                    "source_hash": cached_data.source_hash,
                    "vertex_count": cached_data.graph.get_vertex_count(),
                    "edge_count": cached_data.graph.get_edge_count(),
                    "is_valid": self.is_cache_valid(yaml_path),
                }
            except (pickle.UnpicklingError, AttributeError, EOFError):
                info["initial_state"] = {"error": "corrupted"}

        # Runtime state cache info
        runtime_path = self._get_cache_path(yaml_path, runtime=True)
        if runtime_path.exists():
            try:
                with open(runtime_path, "rb") as f:
                    runtime_data: RuntimeStateData = pickle.load(f)
                info["runtime_state"] = {
                    "cache_path": str(runtime_path),
                    "source_hash": runtime_data.source_hash,
                    "last_modified": runtime_data.last_modified.isoformat(),
                    "modification_count": runtime_data.modification_count,
                    "vertex_count": runtime_data.graph.get_vertex_count(),
                    "edge_count": runtime_data.graph.get_edge_count(),
                    "is_compatible": self.is_runtime_state_compatible(yaml_path),
                }
            except (pickle.UnpicklingError, AttributeError, EOFError):
                info["runtime_state"] = {"error": "corrupted"}

        return info if info else None
