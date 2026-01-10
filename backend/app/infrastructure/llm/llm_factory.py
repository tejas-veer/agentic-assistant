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
    
    async def close(self) -> None:
        """Close the provider and release resources."""
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
                logger.info("[Tejas Test] Initializing Gemini provider...")
                cls._instance = GeminiProvider(api_key=settings.GEMINI_API_KEY)
                logger.info("[Tejas Test] ✅ Gemini LLM initialized successfully")
                return True
            except Exception as e:
                logger.error(f"[Tejas Test] ❌ Failed to initialize Gemini: {e}")
        
        logger.warning("[Tejas Test] ⚠️ No LLM provider configured")
        return False
    
    @classmethod
    def get_provider(cls) -> Optional["LLMProvider"]:
        """Get the initialized LLM provider instance."""
        logger.info("[Tejas Test] Getting LLM provider instance")
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
    async def shutdown(cls) -> None:
        """Shutdown the LLM provider and close connections."""
        logger.info("[Tejas Test] Shutting down LLM provider...")
        if cls._instance is not None:
            try:
                await cls._instance.close()
                logger.info("[Tejas Test] ✅ LLM provider closed")
            except Exception as e:
                logger.error(f"[Tejas Test] ❌ Error closing LLM provider: {e}")
        cls._instance = None
        cls._initialized = False
    
    @classmethod
    def reset(cls) -> None:
        """Reset the factory. Useful for testing."""
        cls._instance = None
        cls._initialized = False


def get_llm_provider() -> Optional[LLMProvider]:
    """Convenience function to get the LLM provider."""
    return LLMFactory.get_provider()
