from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        pass
    
    @abstractmethod
    async def generate_with_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

