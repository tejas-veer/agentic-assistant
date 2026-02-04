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
        self.menu_service = MenuService(session)
        self.cart_service = CartService(session)
        self._current_cart_id: Optional[str] = None
        self._business_id: str = "1"

    def set_business_id(self, business_id: str):
        self._business_id = business_id

    @property
    def llm(self):
        return get_llm_provider()

    @property
    def is_llm_available(self) -> bool:
        return LLMFactory.is_available()

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
            "status": ConversationStatus.ACTIVE.value,
            "llm_available": self.is_llm_available
        }

    async def process_text_input(
        self,
        session_id: str,
        text: str,
        device_id: str,
        business_id: str = "1"
    ) -> Dict[str, Any]:
        self._business_id = business_id
        logger.info("[Tejas Test] " + "=" * 50)
        logger.info("[Tejas Test] 💬 Processing text input")
        logger.info(f"[Tejas Test] 📤 Session: {session_id}")
        logger.info(f"[Tejas Test] 📤 User message: {text}")
        logger.info(f"[Tejas Test] 🤖 LLM available: {self.is_llm_available}")

        await self._save_message(session_id, "user", text)

        menu_text = await self.menu_service.get_menu_for_assistant(business_id)
        cart = await self._get_or_create_cart(session_id, device_id, business_id)
        cart_data = await self.cart_service.get_cart(cart.id) if cart else None
        cart_summary = self._format_cart_summary(cart_data) if cart_data else "Cart is empty."

        log_cart = cart_summary[:100] + "..." if len(cart_summary) > 100 else cart_summary
        logger.info(f"[Tejas Test] 🛒 Cart status: {log_cart}")

        messages = await self._get_conversation_history(session_id)
        logger.info(f"[Tejas Test] 📜 Conversation history: {len(messages)} messages")

        logger.info("[Tejas Test] 🤖 Calling LLM...")
        response = await self._call_llm(menu_text, cart_summary, messages, text)
        logger.info(f"[Tejas Test] 🤖 LLM Response: {json.dumps(response, indent=2)}")

        action_result = await self._execute_action(
            session_id,
            device_id,
            response.get("action"),
            response.get("action_params", {})
        )

        if action_result:
            log_result = json.dumps(action_result, indent=2)[:200]
            logger.info(f"[Tejas Test] ⚡ Action result: {log_result}")

        assistant_response = response.get("response", "I'm sorry, I couldn't process that.")
        if Util.is_not_null(action_result) and action_result.get("error"):
            assistant_response = action_result.get("error")

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
        await self.session.execute(
            update(AssistantSessionModel)
            .where(AssistantSessionModel.session_id == session_id)
            .values(status=ConversationStatus.COMPLETED)
        )
        await self.session.flush()
        return True

    async def _get_or_create_cart(self, session_id: str, device_id: str, business_id: str):
        cart = await self.cart_service.get_cart_by_session(session_id)
        if Util.is_null(cart):
            cart_model = await self.cart_service.get_or_create_cart(
                business_id=business_id,
                session_id=session_id,
                device_id=device_id
            )
            self._current_cart_id = cart_model.id
            return cart_model
        self._current_cart_id = cart.get("id")
        return type('Cart', (), {'id': cart.get("id")})()

    async def _call_llm(
        self,
        menu_text: str,
        cart_summary: str,
        history: List[Dict],
        current_message: str
    ) -> Dict[str, Any]:
        if not self.is_llm_available:
            logger.warning("[Tejas Test] ⚠️ LLM not available - returning fallback response")
            return {
                "response": "AI assistant is not configured. Please use the menu to order manually, or contact staff for help.",
                "action": "none",
                "action_params": {}
            }

        system_prompt = f"{SYSTEM_PROMPT}\n\nMENU:\n{menu_text}\n\nCURRENT CART:\n{cart_summary}"

        messages = []
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": current_message})

        try:
            logger.info("[Tejas Test] Calling LLM generate_with_json...")
            return await self.llm.generate_with_json(system_prompt, messages)
        except Exception as e:
            logger.error(f"[Tejas Test] ❌ LLM error: {e}")
            error_msg = str(e)

            if "429" in error_msg:
                return {
                    "response": "I'm a bit busy right now. Please wait a moment and try again.",
                    "action": "none",
                    "action_params": {}
                }

            if "API error" in error_msg:
                return {
                    "response": "I'm having trouble connecting. Please try again in a moment.",
                    "action": "none",
                    "action_params": {}
                }

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
                if self._current_cart_id:
                    cart = await self.cart_service.get_cart(self._current_cart_id)
                    return {"cart": cart}
                return {"cart": None}

            elif action == "place_order":
                if self._current_cart_id:
                    cart = await self.cart_service.confirm_order(self._current_cart_id)
                    return {"order": cart}
                return {"error": "No cart to place order from."}

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
        item_name = params.get("item_name", "")
        quantity = params.get("quantity", 1)

        items = await self.menu_service.search_menu_items(self._business_id, item_name)
        if Util.is_empty(items):
            return {"error": f"Sorry, I couldn't find '{item_name}' on the menu."}

        item = items[0]

        if not self._current_cart_id:
            cart_model = await self.cart_service.get_or_create_cart(
                business_id=self._business_id,
                session_id=session_id,
                device_id=device_id
            )
            self._current_cart_id = cart_model.id

        cart = await self.cart_service.add_item(
            self._current_cart_id,
            item["id"],
            quantity
        )
        return {"cart": cart, "added_item": item["name"]}

    async def _action_remove_from_cart(
        self,
        session_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        item_name = params.get("item_name", "")
        items = await self.menu_service.search_menu_items(self._business_id, item_name)

        if Util.is_not_empty(items) and self._current_cart_id:
            cart_data = await self.cart_service.get_cart(self._current_cart_id)
            if cart_data and cart_data.get("items"):
                for cart_item in cart_data["items"]:
                    if cart_item["item_id"] == items[0]["id"]:
                        await self.cart_service.remove_item(self._current_cart_id, cart_item["id"])
                        break

        return {"removed": item_name}

    async def _action_update_quantity(
        self,
        session_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        item_name = params.get("item_name", "")
        quantity = params.get("quantity", 1)
        items = await self.menu_service.search_menu_items(self._business_id, item_name)

        if Util.is_not_empty(items) and self._current_cart_id:
            cart_data = await self.cart_service.get_cart(self._current_cart_id)
            if cart_data and cart_data.get("items"):
                for cart_item in cart_data["items"]:
                    if cart_item["item_id"] == items[0]["id"]:
                        cart = await self.cart_service.update_item_quantity(
                            self._current_cart_id,
                            cart_item["id"],
                            quantity
                        )
                        return {"cart": cart}

        return {"error": f"Couldn't find {item_name} in your cart."}

    async def _save_message(self, session_id: str, role: str, content: str):
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
            lines.append(f"- {item['item_name']} x{item['quantity']}: ₹{item['total_price']:.2f}")
        lines.append(f"Subtotal: ₹{cart['subtotal']:.2f}")
        lines.append(f"Tax: ₹{cart['tax']:.2f}")
        lines.append(f"Total: ₹{cart['total']:.2f}")

        return "\n".join(lines)
