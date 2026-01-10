from typing import Dict, Any
import httpx
from .base_provider import CallAgentProviderBase
from app.core.config import settings
from app.utils.null_check import Util


class VapiCallProvider(CallAgentProviderBase):
    def __init__(self):
        self.api_key = settings.VAPI_API_KEY
        self.base_url = "https://api.vapi.ai"
    
    async def initiate_call(self, phone_number: str, context: Dict[str, Any]) -> str:
        if Util.is_null(self.api_key):
            raise ValueError("VAPI API key not configured")
        
        assistant_id = Util.safe_get(context, "assistant_id", "")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/call/phone",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "phoneNumberId": Util.safe_get(context, "phone_number_id"),
                    "customer": {"number": phone_number},
                    "assistantId": assistant_id
                }
            )
            response.raise_for_status()
            data = response.json()
            return Util.safe_get(data, "id", "")
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message_type = Util.safe_get(payload, "message", {}).get("type", "")
        call_id = Util.safe_get(payload, "message", {}).get("call", {}).get("id", "")
        
        return {
            "call_id": call_id,
            "event_type": message_type,
            "payload": payload
        }
    
    async def end_call(self, call_id: str) -> bool:
        if Util.is_null(self.api_key):
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/call/{call_id}/stop",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
    
    async def transfer_call(self, call_id: str, target_number: str) -> bool:
        return False
    
    async def create_assistant(self, name: str, system_prompt: str, first_message: str) -> str:
        if Util.is_null(self.api_key):
            raise ValueError("VAPI API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/assistant",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": name,
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "messages": [{"role": "system", "content": system_prompt}]
                    },
                    "voice": {"provider": "11labs", "voiceId": "burt"},
                    "firstMessage": first_message
                }
            )
            response.raise_for_status()
            data = response.json()
            return Util.safe_get(data, "id", "")

