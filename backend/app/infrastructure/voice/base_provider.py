from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator


class VoiceProviderBase(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        pass
    
    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: str = "en") -> AsyncIterator[str]:
        pass


class TextToSpeechProviderBase(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        pass
    
    @abstractmethod
    async def synthesize_stream(self, text: str, voice_id: Optional[str] = None) -> AsyncIterator[bytes]:
        pass

