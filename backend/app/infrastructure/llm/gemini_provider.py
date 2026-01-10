from typing import List, Dict, Any
import httpx
import json
import logging
from app.core.config import settings
from app.utils.null_check import Util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini")


class GeminiProvider:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-lite"
    
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        if Util.is_null(self.api_key):
            raise ValueError("Gemini API key not configured")
        
        contents = []
        
        contents.append({
            "role": "user",
            "parts": [{"text": f"System Instructions: {system_prompt}"}]
        })
        contents.append({
            "role": "model", 
            "parts": [{"text": "I understand. I will follow these instructions."}]
        })
        
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        logger.info("=" * 60)
        logger.info("🤖 [GEMINI] Sending request to Gemini API")
        logger.info(f"📤 Model: {self.model}")
        logger.info(f"📤 Messages count: {len(messages)}")
        if messages:
            logger.info(f"📤 Last message: {messages[-1].get('content', '')[:100]}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                },
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": 1024,
                    }
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"❌ [GEMINI] API error: {response.status_code}")
                logger.error(f"❌ [GEMINI] Response: {response.text}")
                raise Exception(f"Gemini API error: {response.status_code}")
            
            data = response.json()
            
            if "candidates" not in data or len(data["candidates"]) == 0:
                logger.error(f"❌ [GEMINI] No candidates in response: {data}")
                raise Exception("No response from Gemini")
            
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            logger.info(f"✅ [GEMINI] Response received")
            logger.info(f"📥 Response text: {text[:200]}..." if len(text) > 200 else f"📥 Response text: {text}")
            logger.info("=" * 60)
            return text
    
    async def generate_with_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        json_instruction = """

CRITICAL: Respond ONLY with a valid JSON object. Nothing else before or after.
Format: {"response": "your friendly message", "action": "none", "action_params": {}}
Actions: none, add_to_cart, remove_from_cart, update_quantity, view_cart, place_order
For add_to_cart: action_params = {"item_name": "name", "quantity": 1}
"""
        
        result = await self.generate(
            system_prompt + json_instruction,
            messages,
            temperature
        )
        
        result = result.strip()
        
        if result.startswith("```"):
            lines = result.split("\n")
            if lines[-1].strip() == "```":
                result = "\n".join(lines[1:-1])
            else:
                result = "\n".join(lines[1:])
            result = result.strip()
        
        json_start = result.find('{')
        json_end = result.rfind('}')
        
        if json_start != -1 and json_end != -1:
            json_str = result[json_start:json_end + 1]
            try:
                parsed = json.loads(json_str)
                if "response" in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            clean_text = result
            if '{' in clean_text:
                clean_text = clean_text[:clean_text.find('{')].strip()
            return {
                "response": clean_text if clean_text else result,
                "action": "none",
                "action_params": {}
            }
