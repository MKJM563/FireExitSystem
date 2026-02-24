from __future__ import annotations
import json
from abc import ABC, abstractmethod
from datetime import datetime

from src.messaging.message_type import MessageType


class Message(ABC):
    def __init__(self, message_type: MessageType) -> None:
        self._timestamp: datetime = datetime.now()
        self._message_type: MessageType = message_type

    def get_type(self) -> MessageType:
        return self._message_type

    def get_timestamp(self) -> datetime:
        return self._timestamp

    @abstractmethod
    def serialize(self) -> bytes:
        pass
