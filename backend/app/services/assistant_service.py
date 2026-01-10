"""
Assistant Service - Handles AI assistant interactions for ordering.
"""

import json
import logging
import uuid
from typing import Optional, Dict, Any, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import AssistantSessionModel, ConversationMessageModel
from app.infrastructure.llm import LLMFactory, get_llm_provider
from app.domain.shared.enums import AssistantType, ConversationStatus
from app.utils.null_check import Util
from app.services.menu_service import MenuService
from app.services.cart_service import CartService
from app.services.order_service import OrderService

logger = logging.getLogger("assistant")


SYSTEM_PROMPT = """You are a helpful voice assistant for a restaurant ordering kiosk. Your role is to help customers place orders.

You have access to the following capabilities:
1. Show the menu and describe items
2. Add items to cart (use action: "add_to_cart" with action_params: {"item_name": "item name", "quantity": 1})
3. Modify quantities in cart (use action: "update_quantity" with action_params: {"item_name": "item name", "quantity": 2})
4. Remove items from cart (use action: "remove_from_cart" with action_params: {"item_name": "item name"})
5. Review the current cart (use action: "view_cart")
6. Place the order (use action: "place_order")

Be friendly, concise, and helpful. Confirm items before adding them. Always mention prices when discussing menu items.
When the customer seems ready, ask if they want to review their order or proceed to checkout.
Use "none" for action when just responding conversationally.

Current menu will be provided in the conversation context."""


class AssistantService:
    """
    Service for handling AI assistant interactions.
    
    Uses the LLM factory to get the configured LLM provider.
    Handles conversation history, cart operations, and order placement.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize AssistantService.
        
        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session
        self.menu_service = MenuService(session)
        self.cart_service = CartService(session)
        self.order_service = OrderService(session)
    
    @property
    def llm(self):
        """Get the LLM provider from factory. Returns None if not configured."""
        return get_llm_provider()
    
    @property
    def is_llm_available(self) -> bool:
        """Check if LLM is available."""
        return LLMFactory.is_available()
    
    async def create_session(
        self,
        assistant_type: AssistantType,
        device_id: str = None,
        phone_number: str = None
    ) -> Dict[str, Any]:
        """Create a new assistant session."""
        session_id = str(uuid.uuid4())
        
        assistant_session = AssistantSessionModel(
            session_id=session_id,
            assistant_type=assistant_type,
            device_id=device_id,
            phone_number=phone_number,
            status=ConversationStatus.ACTIVE,
            context={"pending_items": [], "confirmed_items": []}
        )
        
        self.session.add(assistant_session)
        await self.session.flush()
        
        return {
            "session_id": session_id,
            "assistant_type": assistant_type.value,
            "status": ConversationStatus.ACTIVE.value,
            "llm_available": self.is_llm_available
        }
    
    async def process_text_input(
        self,
        session_id: str,
        text: str,
        device_id: str
    ) -> Dict[str, Any]:
        """
        Process text input from the user.
        
        Args:
            session_id: The session ID
            text: User's text input
            device_id: Device identifier
        
        Returns:
            Response dict with 'response', 'transcript', 'action', 'action_result'
        """
        logger.info("[Tejas Test] " + "=" * 50)
        logger.info("[Tejas Test] 💬 Processing text input")
        logger.info(f"[Tejas Test] 📤 Session: {session_id}")
        logger.info(f"[Tejas Test] 📤 User message: {text}")
        logger.info(f"[Tejas Test] 🤖 LLM available: {self.is_llm_available}")
        
        # Save user message
        await self._save_message(session_id, "user", text)
        
        # Get context
        menu_text = await self.menu_service.get_menu_for_assistant()
        cart = await self.cart_service.get_cart(session_id)
        cart_summary = self._format_cart_summary(cart) if cart else "Cart is empty."
        
        log_cart = cart_summary[:100] + "..." if len(cart_summary) > 100 else cart_summary
        logger.info(f"[Tejas Test] 🛒 Cart status: {log_cart}")
        
        messages = await self._get_conversation_history(session_id)
        logger.info(f"[Tejas Test] 📜 Conversation history: {len(messages)} messages")
        
        logger.info("[Tejas Test] 🤖 Calling LLM...")
        response = await self._call_llm(menu_text, cart_summary, messages, text)
        logger.info(f"[Tejas Test] 🤖 LLM Response: {json.dumps(response, indent=2)}")
        
        # Execute action if any
        action_result = await self._execute_action(
            session_id,
            device_id,
            response.get("action"),
            response.get("action_params", {})
        )
        
        if action_result:
            log_result = json.dumps(action_result, indent=2)[:200]
            logger.info(f"[Tejas Test] ⚡ Action result: {log_result}")
        
        # Prepare final response
        assistant_response = response.get("response", "I'm sorry, I couldn't process that.")
        if Util.is_not_null(action_result) and action_result.get("error"):
            assistant_response = action_result.get("error")
        
        # Save assistant response
        await self._save_message(session_id, "assistant", assistant_response)
        
        result = {
            "response": assistant_response,
            "transcript": text,
            "action": response.get("action"),
            "action_result": action_result
        }
        
        log_response = assistant_response[:100] + "..." if len(assistant_response) > 100 else assistant_response
        logger.info(f"[Tejas Test] 📥 Final response: {log_response}")
        logger.info("[Tejas Test] " + "=" * 50)
        
        return result
    
    async def end_session(self, session_id: str) -> bool:
        """End an assistant session."""
        await self.session.execute(
            update(AssistantSessionModel)
            .where(AssistantSessionModel.session_id == session_id)
            .values(status=ConversationStatus.COMPLETED)
        )
        await self.session.flush()
        return True
    
    async def _call_llm(
        self,
        menu_text: str,
        cart_summary: str,
        history: List[Dict],
        current_message: str
    ) -> Dict[str, Any]:
        """
        Call the LLM provider.
        
        Returns a fallback response if LLM is not available.
        """
        # Check if LLM is available
        if not self.is_llm_available:
            logger.warning("[Tejas Test] ⚠️ LLM not available - returning fallback response")
            return {
                "response": "AI assistant is not configured. Please use the menu to order manually, or contact staff for help.",
                "action": "none",
                "action_params": {}
            }
        
        # Build system prompt with context
        system_prompt = f"{SYSTEM_PROMPT}\n\nMENU:\n{menu_text}\n\nCURRENT CART:\n{cart_summary}"
        
        # Build messages
        messages = []
        for msg in history[-10:]:  # Last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": current_message})
        
        try:
            logger.info("[Tejas Test] Calling LLM generate_with_json...")
            return await self.llm.generate_with_json(system_prompt, messages)
        except Exception as e:
            logger.error(f"[Tejas Test] ❌ LLM error: {e}")
            error_msg = str(e)
            
            # Handle rate limiting
            if "429" in error_msg:
                return {
                    "response": "I'm a bit busy right now. Please wait a moment and try again.",
                    "action": "none",
                    "action_params": {}
                }
            
            # Handle API errors
            if "API error" in error_msg:
                return {
                    "response": "I'm having trouble connecting. Please try again in a moment.",
                    "action": "none",
                    "action_params": {}
                }
            
            # Generic error
            return {
                "response": "I'm having trouble right now. Please try again.",
                "action": "none",
                "action_params": {}
            }
    
    async def _execute_action(
        self,
        session_id: str,
        device_id: str,
        action: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute an action based on LLM response."""
        if Util.is_null(action) or action == "none":
            return None
        
        try:
            if action == "add_to_cart":
                return await self._action_add_to_cart(session_id, device_id, params)
            
            elif action == "remove_from_cart":
                return await self._action_remove_from_cart(session_id, params)
            
            elif action == "update_quantity":
                return await self._action_update_quantity(session_id, params)
            
            elif action == "view_cart":
                cart = await self.cart_service.get_cart(session_id)
                return {"cart": cart}
            
            elif action == "place_order":
                order = await self.order_service.create_order_from_cart(
                    session_id,
                    assistant_session_id=session_id
                )
                return {"order": order}
            
        except Exception as e:
            logger.error(f"❌ Action error: {e}")
            return {"error": str(e)}
        
        return None
    
    async def _action_add_to_cart(
        self,
        session_id: str,
        device_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_cart action."""
        item_name = params.get("item_name", "")
        quantity = params.get("quantity", 1)
        
        items = await self.menu_service.search_menu_items(item_name)
        if Util.is_empty(items):
            return {"error": f"Sorry, I couldn't find '{item_name}' on the menu."}
        
        item = items[0]
        cart = await self.cart_service.add_item(
            session_id,
            device_id,
            item["id"],
            quantity
        )
        return {"cart": cart, "added_item": item["name"]}
    
    async def _action_remove_from_cart(
        self,
        session_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle remove_from_cart action."""
        item_name = params.get("item_name", "")
        items = await self.menu_service.search_menu_items(item_name)
        if Util.is_not_empty(items):
            await self.cart_service.remove_item(session_id, items[0]["id"])
        return {"removed": item_name}
    
    async def _action_update_quantity(
        self,
        session_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle update_quantity action."""
        item_name = params.get("item_name", "")
        quantity = params.get("quantity", 1)
        items = await self.menu_service.search_menu_items(item_name)
        if Util.is_not_empty(items):
            cart = await self.cart_service.update_item_quantity(
                session_id,
                items[0]["id"],
                quantity
            )
            return {"cart": cart}
        return {"error": f"Couldn't find {item_name} in your cart."}
    
    async def _save_message(self, session_id: str, role: str, content: str):
        """Save a message to the conversation history."""
        result = await self.session.execute(
            select(AssistantSessionModel).where(AssistantSessionModel.session_id == session_id)
        )
        assistant_session = result.scalar_one_or_none()
        
        if Util.is_not_null(assistant_session):
            message = ConversationMessageModel(
                session_id=assistant_session.id,
                role=role,
                content=content
            )
            self.session.add(message)
            await self.session.flush()
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        result = await self.session.execute(
            select(AssistantSessionModel).where(AssistantSessionModel.session_id == session_id)
        )
        assistant_session = result.scalar_one_or_none()
        
        if Util.is_null(assistant_session):
            return []
        
        result = await self.session.execute(
            select(ConversationMessageModel)
            .where(ConversationMessageModel.session_id == assistant_session.id)
            .order_by(ConversationMessageModel.created_at)
        )
        messages = result.scalars().all()
        
        return [{"role": m.role, "content": m.content} for m in messages]
    
    def _format_cart_summary(self, cart: Dict[str, Any]) -> str:
        """Format cart as text summary for LLM context."""
        if Util.is_null(cart) or Util.is_empty(cart.get("items")):
            return "Cart is empty."
        
        lines = ["Current Cart:"]
        for item in cart["items"]:
            lines.append(f"- {item['menu_item_name']} x{item['quantity']}: ₹{item['total_price']:.2f}")
        lines.append(f"Subtotal: ₹{cart['subtotal']:.2f}")
        lines.append(f"Tax: ₹{cart['tax']:.2f}")
        lines.append(f"Total: ₹{cart['total']:.2f}")
        
        return "\n".join(lines)
