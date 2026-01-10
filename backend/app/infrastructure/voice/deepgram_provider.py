from typing import Optional, AsyncIterator
import httpx
from .base_provider import VoiceProviderBase
from app.core.config import settings
from app.utils.null_check import Util


class DeepgramProvider(VoiceProviderBase):
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        self.base_url = "https://api.deepgram.com/v1"
    
    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        if Util.is_null(self.api_key):
            raise ValueError("Deepgram API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/listen",
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "audio/wav"
                },
                params={
                    "language": language,
                    "model": "nova-2",
                    "smart_format": "true"
                },
                content=audio_data
            )
            response.raise_for_status()
            data = response.json()
            
            transcript = Util.safe_get(
                Util.safe_list_get(
                    Util.safe_get(
                        Util.safe_list_get(
                            Util.safe_get(data, "results", {}).get("channels", []),
                            0, {}
                        ),
                        "alternatives", []
                    ),
                    0, {}
                ),
                "transcript", ""
            )
            return transcript
    
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: str = "en") -> AsyncIterator[str]:
        pass

