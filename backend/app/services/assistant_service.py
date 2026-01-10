from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging
from app.infrastructure.database.models import AssistantSessionModel, ConversationMessageModel
from app.infrastructure.llm.gemini_provider import GeminiProvider
from app.domain.shared.enums import AssistantType, ConversationStatus
from app.core.config import settings
from app.utils.null_check import Util
from app.services.menu_service import MenuService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
import uuid

logging.basicConfig(level=logging.INFO)
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
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm = GeminiProvider()
        self.menu_service = MenuService(session)
        self.cart_service = CartService(session)
        self.order_service = OrderService(session)
    
    async def create_session(
        self,
        assistant_type: AssistantType,
        device_id: str = None,
        phone_number: str = None
    ) -> Dict[str, Any]:
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
            "status": ConversationStatus.ACTIVE.value
        }
    
    async def process_text_input(
        self,
        session_id: str,
        text: str,
        device_id: str
    ) -> Dict[str, Any]:
        logger.info("=" * 60)
        logger.info("💬 [ASSISTANT] Processing text input")
        logger.info(f"📤 Session: {session_id}")
        logger.info(f"📤 User message: {text}")
        
        await self._save_message(session_id, "user", text)
        
        menu_text = await self.menu_service.get_menu_for_assistant()
        cart = await self.cart_service.get_cart(session_id)
        cart_summary = self._format_cart_summary(cart) if cart else "Cart is empty."
        logger.info(f"🛒 Cart status: {cart_summary[:100]}..." if len(cart_summary) > 100 else f"🛒 Cart status: {cart_summary}")
        
        messages = await self._get_conversation_history(session_id)
        logger.info(f"📜 Conversation history: {len(messages)} messages")
        
        response = await self._call_llm(menu_text, cart_summary, messages, text)
        logger.info(f"🤖 LLM Response: {json.dumps(response, indent=2)}")
        
        action_result = await self._execute_action(
            session_id,
            device_id,
            response.get("action"),
            response.get("action_params", {})
        )
        
        if action_result:
            logger.info(f"⚡ Action result: {json.dumps(action_result, indent=2)[:200]}")
        
        assistant_response = response.get("response", "I'm sorry, I couldn't process that.")
        if Util.is_not_null(action_result):
            if action_result.get("error"):
                assistant_response = action_result.get("error")
        
        await self._save_message(session_id, "assistant", assistant_response)
        
        result = {
            "response": assistant_response,
            "transcript": text,
            "action": response.get("action"),
            "action_result": action_result
        }
        
        logger.info(f"📥 Final response: {assistant_response[:100]}..." if len(assistant_response) > 100 else f"📥 Final response: {assistant_response}")
        logger.info("=" * 60)
        
        return result
    
    async def end_session(self, session_id: str) -> bool:
        from sqlalchemy import select, update
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
        if Util.is_null(settings.GEMINI_API_KEY):
            return {
                "response": "AI service not configured. Please use manual ordering.",
                "action": "none"
            }
        
        system_prompt = f"{SYSTEM_PROMPT}\n\nMENU:\n{menu_text}\n\nCURRENT CART:\n{cart_summary}"
        
        messages = []
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": current_message})
        
        try:
            return await self.llm.generate_with_json(system_prompt, messages)
        except Exception as e:
            import logging
            logging.error(f"LLM error: {e}")
            error_msg = str(e)
            if "429" in error_msg:
                return {
                    "response": "I'm a bit busy right now. Please wait a moment and try again.",
                    "action": "none"
                }
            return {
                "response": f"I'm having trouble right now. Please try again.",
                "action": "none"
            }
    
    async def _execute_action(
        self,
        session_id: str,
        device_id: str,
        action: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if Util.is_null(action) or action == "none":
            return None
        
        try:
            if action == "add_to_cart":
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
            
            elif action == "remove_from_cart":
                item_name = params.get("item_name", "")
                items = await self.menu_service.search_menu_items(item_name)
                if Util.is_not_empty(items):
                    await self.cart_service.remove_item(session_id, items[0]["id"])
                return {"removed": item_name}
            
            elif action == "update_quantity":
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
            return {"error": str(e)}
        
        return None
    
    async def _save_message(self, session_id: str, role: str, content: str):
        from sqlalchemy import select
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
        from sqlalchemy import select
        
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
        if Util.is_null(cart) or Util.is_empty(cart.get("items")):
            return "Cart is empty."
        
        lines = ["Current Cart:"]
        for item in cart["items"]:
            lines.append(f"- {item['menu_item_name']} x{item['quantity']}: ${item['total_price']:.2f}")
        lines.append(f"Subtotal: ${cart['subtotal']:.2f}")
        lines.append(f"Tax: ${cart['tax']:.2f}")
        lines.append(f"Total: ${cart['total']:.2f}")
        
        return "\n".join(lines)

