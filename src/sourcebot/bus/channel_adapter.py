# sourcebot/bus/channel_adapter.py
from .message_models from OutboundMessage, InboundMessage
from .event_bus from EventBus
from typing import Any
from abc import ABC, abstractmethod

class ChannelAdapter(ABC):
    def __init__(self, bus: EventBus):
        self.bus = bus

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def send(self, msg: OutboundMessage):
        pass

    @abstractmethod
    def normalize(self, raw_event: Any) -> InboundMessage:
        pass