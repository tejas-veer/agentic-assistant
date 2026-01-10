"""Gemini LLM Provider - Google's Gemini API integration."""

import json
import logging
from typing import List, Dict, Any

import httpx

logger = logging.getLogger("gemini")


class GeminiProvider:
    """
    Gemini LLM Provider.
    
    Uses Google's Gemini API for text generation.
    API key is injected via constructor for better testability.
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    DEFAULT_MODEL = "gemini-2.5-flash-lite"
    
    def __init__(self, api_key: str, model: str = None):
        """
        Initialize GeminiProvider.
        
        Args:
            api_key: Google Gemini API key (required)
            model: Model name (optional, defaults to gemini-2.5-flash-lite)
        
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key or not api_key.strip():
            raise ValueError("Gemini API key is required")
        
        self.api_key = api_key.strip()
        self.model = model or self.DEFAULT_MODEL
        self._client: httpx.AsyncClient = None
        
        logger.info(f"[Tejas Test] GeminiProvider initialized with model: {self.model}")
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            logger.info("[Tejas Test] Creating new HTTP client")
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        if self._client is not None:
            logger.info("[Tejas Test] Closing HTTP client")
            await self._client.aclose()
            self._client = None
    
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Generate a text response.
        
        Args:
            system_prompt: System instructions for the model
            messages: List of conversation messages with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
        
        Returns:
            Generated text response
        
        Raises:
            Exception: On API errors
        """
        contents = self._build_contents(system_prompt, messages)
        
        logger.info("[Tejas Test] " + "=" * 50)
        logger.info("[Tejas Test] 🤖 Sending request to Gemini")
        logger.info(f"[Tejas Test] 📤 Model: {self.model}")
        logger.info(f"[Tejas Test] 📤 Messages count: {len(messages)}")
        if messages:
            last_msg = messages[-1].get('content', '')[:100]
            logger.info(f"[Tejas Test] 📤 Last message: {last_msg}...")
        
        client = await self._get_client()
        response = await client.post(
            f"{self.BASE_URL}/models/{self.model}:generateContent",
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
            }
        )
        
        if response.status_code != 200:
            logger.error(f"[Tejas Test] ❌ API error: {response.status_code}")
            logger.error(f"[Tejas Test] ❌ Response: {response.text}")
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        logger.info(f"[Tejas Test] ✅ API call successful, status: {response.status_code}")
        data = response.json()
        
        if "candidates" not in data or len(data["candidates"]) == 0:
            logger.error(f"[Tejas Test] ❌ No candidates in response: {data}")
            raise Exception("No response from Gemini")
        
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        log_text = text[:200] + "..." if len(text) > 200 else text
        logger.info(f"[Tejas Test] ✅ Response received")
        logger.info(f"[Tejas Test] 📥 Response: {log_text}")
        logger.info("[Tejas Test] " + "=" * 50)
        
        return text
    
    async def generate_with_json(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a JSON response.
        
        Args:
            system_prompt: System instructions for the model
            messages: List of conversation messages
            temperature: Sampling temperature
        
        Returns:
            Parsed JSON response with 'response', 'action', 'action_params'
        """
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
        logger.info(f"[Tejas Test] 🤖 Raw JSON response: {result}")
        return self._parse_json_response(result)
    
    def _build_contents(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]]
    ) -> List[Dict]:
        """Build the contents array for Gemini API."""
        logger.info(f"[Tejas Test] Building contents with {len(messages)} messages")
        contents = [
            {
                "role": "user",
                "parts": [{"text": f"System Instructions: {system_prompt}"}]
            },
            {
                "role": "model",
                "parts": [{"text": "I understand. I will follow these instructions."}]
            }
        ]
        
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        return contents
    
    def _parse_json_response(self, result: str) -> Dict[str, Any]:
        """Parse JSON from the model response, handling various formats."""
        logger.info("[Tejas Test] Parsing JSON response")
        result = result.strip()
        
        # Remove markdown code blocks
        if result.startswith("```"):
            lines = result.split("\n")
            if lines[-1].strip() == "```":
                result = "\n".join(lines[1:-1])
            else:
                result = "\n".join(lines[1:])
            result = result.strip()
        
        # Extract JSON object
        json_start = result.find('{')
        json_end = result.rfind('}')
        
        if json_start != -1 and json_end != -1:
            json_str = result[json_start:json_end + 1]
            try:
                parsed = json.loads(json_str)
                if "response" in parsed:
                    logger.info(f"[Tejas Test] ✅ Parsed JSON successfully, action: {parsed.get('action', 'none')}")
                    return parsed
            except json.JSONDecodeError:
                logger.warning("[Tejas Test] ⚠️ JSON decode failed for extracted string")
        
        try:
            parsed = json.loads(result)
            logger.info(f"[Tejas Test] ✅ Direct JSON parse successful")
            return parsed
        except json.JSONDecodeError:
            logger.warning("[Tejas Test] ⚠️ Fallback: treating as plain text")
            clean_text = result
            if '{' in clean_text:
                clean_text = clean_text[:clean_text.find('{')].strip()
            return {
                "response": clean_text if clean_text else result,
                "action": "none",
                "action_params": {}
            }
