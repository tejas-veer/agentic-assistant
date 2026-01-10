from typing import Dict, Any
import httpx
from .base_provider import CallAgentProviderBase
from app.core.config import settings
from app.utils.null_check import Util


class TwilioCallProvider(CallAgentProviderBase):
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
    
    async def initiate_call(self, phone_number: str, context: Dict[str, Any]) -> str:
        if Util.is_null(self.account_sid) or Util.is_null(self.auth_token):
            raise ValueError("Twilio credentials not configured")
        
        webhook_url = Util.safe_get(context, "webhook_url", "")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Calls.json",
                auth=(self.account_sid, self.auth_token),
                data={
                    "To": phone_number,
                    "From": self.phone_number,
                    "Url": webhook_url
                }
            )
            response.raise_for_status()
            data = response.json()
            return Util.safe_get(data, "sid", "")
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        call_status = Util.safe_get(payload, "CallStatus", "")
        call_sid = Util.safe_get(payload, "CallSid", "")
        speech_result = Util.safe_get(payload, "SpeechResult", "")
        
        return {
            "call_id": call_sid,
            "status": call_status,
            "transcript": speech_result
        }
    
    async def end_call(self, call_id: str) -> bool:
        if Util.is_null(self.account_sid) or Util.is_null(self.auth_token):
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Calls/{call_id}.json",
                auth=(self.account_sid, self.auth_token),
                data={"Status": "completed"}
            )
            return response.status_code == 200
    
    async def transfer_call(self, call_id: str, target_number: str) -> bool:
        return False
    
    def generate_twiml_response(self, message: str, gather_speech: bool = True) -> str:
        if gather_speech:
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" timeout="5" speechTimeout="auto">
        <Say>{message}</Say>
    </Gather>
</Response>"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{message}</Say>
</Response>"""

