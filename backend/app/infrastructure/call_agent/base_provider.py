from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable


class CallAgentProviderBase(ABC):
    @abstractmethod
    async def initiate_call(self, phone_number: str, context: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def end_call(self, call_id: str) -> bool:
        pass
    
    @abstractmethod
    async def transfer_call(self, call_id: str, target_number: str) -> bool:
        pass

