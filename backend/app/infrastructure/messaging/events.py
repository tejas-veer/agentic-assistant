from typing import Dict, Any, Callable, List
from enum import Enum
import asyncio


class EventType(str, Enum):
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    ORDER_STATUS_CHANGED = "order.status_changed"
    CART_UPDATED = "cart.updated"
    ASSISTANT_MESSAGE = "assistant.message"
    CALL_STARTED = "call.started"
    CALL_ENDED = "call.ended"


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, handler: Callable):
        if event_type.value not in self._handlers:
            self._handlers[event_type.value] = []
        self._handlers[event_type.value].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        if event_type.value in self._handlers:
            self._handlers[event_type.value].remove(handler)
    
    async def publish(self, event_type: EventType, data: Dict[str, Any]):
        handlers = self._handlers.get(event_type.value, [])
        tasks = []
        
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(data))
            else:
                handler(data)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


event_bus = EventBus()

