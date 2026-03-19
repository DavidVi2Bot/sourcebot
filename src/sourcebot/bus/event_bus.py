# sourcebot/bus/event_bus.py
import asyncio
from typing import Any, Callable, Dict, List, Type, Coroutine
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.handlers: Dict[Type, List[Callable[[Any], Coroutine]]] = defaultdict(list)

    def subscribe(self, event_type: Type, handler: Callable[[Any], Coroutine]):
        self.handlers[event_type].append(handler)

    async def publish(self, event: Any):
        if type(event) in self.handlers:
            await asyncio.gather(*(h(event) for h in self.handlers[type(event)]))