"""
LLM Factory - Creates and manages LLM provider instances.

Uses the factory pattern to abstract LLM provider creation.
Currently supports Gemini, extensible for other providers.
"""

import logging
from typing import Optional, Protocol, Dict, Any, List

from app.core.config import settings

logger = logging.getLogger("llm")


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers."""
    
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """Generate a text response."""
        ...
    
    async def generate_with_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate a JSON response."""
        ...


class LLMFactory:
    """Factory for creating LLM provider instances."""
    
    _instance: Optional["LLMProvider"] = None
    _initialized: bool = False
    
    @classmethod
    def initialize(cls) -> bool:
        """
        Initialize the LLM provider at application startup.
        Returns True if successful, False otherwise.
        """
        if cls._initialized:
            return cls._instance is not None
        
        cls._initialized = True
        
        if settings.GEMINI_API_KEY:
            try:
                from .gemini_provider import GeminiProvider
                cls._instance = GeminiProvider(api_key=settings.GEMINI_API_KEY)
                logger.info("✅ Gemini LLM initialized")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
        
        logger.warning("⚠️ No LLM provider configured")
        return False
    
    @classmethod
    def get_provider(cls) -> Optional["LLMProvider"]:
        """Get the initialized LLM provider instance."""
        if not cls._initialized:
            cls.initialize()
        return cls._instance
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if an LLM provider is available."""
        if not cls._initialized:
            cls.initialize()
        return cls._instance is not None
    
    @classmethod
    def reset(cls) -> None:
        """Reset the factory. Useful for testing or shutdown."""
        cls._instance = None
        cls._initialized = False


def get_llm_provider() -> Optional[LLMProvider]:
    """Convenience function to get the LLM provider."""
    return LLMFactory.get_provider()
