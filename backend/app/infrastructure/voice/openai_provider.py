from typing import Optional, AsyncIterator
import httpx
import io
from .base_provider import VoiceProviderBase, TextToSpeechProviderBase
from app.core.config import settings
from app.utils.null_check import Util


class OpenAIWhisperProvider(VoiceProviderBase):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
    
    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        if Util.is_null(self.api_key):
            raise ValueError("OpenAI API key not configured")
        
        async with httpx.AsyncClient() as client:
            files = {"file": ("audio.wav", io.BytesIO(audio_data), "audio/wav")}
            data = {"model": "whisper-1", "language": language}
            
            response = await client.post(
                f"{self.base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return Util.safe_get(result, "text", "")
    
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: str = "en") -> AsyncIterator[str]:
        pass


class OpenAITTSProvider(TextToSpeechProviderBase):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
    
    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        if Util.is_null(self.api_key):
            raise ValueError("OpenAI API key not configured")
        
        voice = Util.get_or_default(voice_id, "alloy")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/audio/speech",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1",
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3"
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.content
    
    async def synthesize_stream(self, text: str, voice_id: Optional[str] = None) -> AsyncIterator[bytes]:
        pass

