# sourcebot/bus/outbound_dispatcher.py
from .message_models from OutboundMessage
from .channel_adapter from ChannelAdapter
from typing import Dict

class OutboundDispatcher:
    def __init__(self, adapters: Dict[str, ChannelAdapter]):
        self.adapters = adapters

    async def dispatch(self, msg: OutboundMessage):
        adapter = self.adapters.get(msg.channel)
        if not adapter:
            print(f"[WARN] No adapter for channel {msg.channel}")
            return
        await adapter.send(msg)