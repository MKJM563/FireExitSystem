from __future__ import annotations
import heapq
import logging
import threading
from datetime import timedelta
from typing import Callable, List, Optional
import time

_logger = logging.getLogger(__name__)


class ScheduledTask:
    def __init__(self, task_id: int, run_at: float, task: Callable, interval: Optional[float] = None) -> None:
        self.task_id: int = task_id
        self.run_at: float = run_at
        self.task: Callable = task
        self.interval: Optional[float] = interval  # seconds; None means one-shot
        self.cancelled: bool = False

    def __lt__(self, other: "ScheduledTask") -> bool:
        return self.run_at < other.run_at


class Scheduler:
    def __init__(self) -> None:
        self._scheduled_tasks: List[ScheduledTask] = []
        self._lock: threading.Lock = threading.Lock()
        self._next_id: int = 0
        # Track cancelled task IDs separately so cancellation survives re-scheduling
        self._cancelled_ids: set = set()

    def schedule(self, task: Callable, delay: timedelta) -> int:
        """Schedule a one-shot task after delay. Returns task ID."""
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            run_at = time.monotonic() + delay.total_seconds()
            scheduled = ScheduledTask(task_id, run_at, task, interval=None)
            heapq.heappush(self._scheduled_tasks, scheduled)
        return task_id

    def schedule_repeating(self, task: Callable, interval: timedelta) -> int:
        """Schedule a repeating task. Returns task ID."""
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            run_at = time.monotonic() + interval.total_seconds()
            scheduled = ScheduledTask(task_id, run_at, task, interval=interval.total_seconds())
            heapq.heappush(self._scheduled_tasks, scheduled)
        return task_id

    def cancel(self, task_id: int) -> None:
        with self._lock:
            self._cancelled_ids.add(task_id)
            for task in self._scheduled_tasks:
                if task.task_id == task_id:
                    task.cancelled = True

    def execute_ready_tasks(self) -> None:
        """Execute all tasks whose run_at time has passed."""
        now = time.monotonic()
        ready: List[ScheduledTask] = []
        with self._lock:
            while self._scheduled_tasks and self._scheduled_tasks[0].run_at <= now:
                task = heapq.heappop(self._scheduled_tasks)
                if not task.cancelled and task.task_id not in self._cancelled_ids:
                    ready.append(task)

        for task in ready:
            try:
                task.task()
            except Exception as exc:
                _logger.error("Exception in scheduled task %d: %s", task.task_id, exc, exc_info=True)
            # Re-schedule repeating tasks; check against cancelled_ids set to avoid
            # a race where cancel() is called after the task is popped from the heap
            if task.interval is not None:
                with self._lock:
                    if task.task_id not in self._cancelled_ids:
                        new_task = ScheduledTask(
                            task.task_id,
                            time.monotonic() + task.interval,
                            task.task,
                            interval=task.interval,
                        )
                        heapq.heappush(self._scheduled_tasks, new_task)
