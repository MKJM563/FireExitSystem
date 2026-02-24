import queue
from typing import Optional

from src.messaging.message import Message


class MessageQueue:
    def __init__(self, max_size: int) -> None:
        self._max_size: int = max_size
        self._queue: queue.Queue = queue.Queue(maxsize=max_size)

    def enqueue(self, message: Message) -> bool:
        try:
            self._queue.put_nowait(message)
            return True
        except queue.Full:
            return False

    def dequeue(self) -> Optional[Message]:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def is_empty(self) -> bool:
        return self._queue.empty()

    def get_size(self) -> int:
        return self._queue.qsize()
