from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.infrastructure.database.repositories import CartRepository, CartItemRepository, MenuRepository
from app.infrastructure.database.models import CartModel, CartItemModel
from app.domain.shared.enums import CartStatus, CartItemStatus, OrderSource, IntentType
from app.infrastructure.messaging.websocket_manager import connection_manager
from app.infrastructure.messaging.events import event_bus, EventType
from app.utils.null_check import Util


TAX_RATE = Decimal("0.10")


class CartService:
    def __init__(self, session: AsyncSession):
        self.cart_repo = CartRepository(session)
        self.cart_item_repo = CartItemRepository(session)
        self.menu_repo = MenuRepository(session)
        self.session = session

    async def get_or_create_cart(
        self,
        business_id: str,
        session_id: str = None,
        device_id: str = None,
        user_id: str = None
    ) -> CartModel:
        if session_id:
            cart = await self.cart_repo.get_by_session(session_id)
            if Util.is_not_null(cart):
                return cart

        cart = CartModel(
            business_id=business_id,
            session_id=session_id,
            device_id=device_id,
            user_id=user_id,
            status=CartStatus.DRAFT,
            source=OrderSource.APP,
            intent=IntentType.FOOD_ORDER,
            item_count=0,
            subtotal=Decimal("0.00"),
            tax=Decimal("0.00"),
            total=Decimal("0.00")
        )
        cart = await self.cart_repo.create(cart)
        return cart

    async def add_item(
        self,
        cart_id: str,
        menu_item_id: str,
        quantity: int = 1,
        notes: str = None
    ) -> Dict[str, Any]:
        cart = await self.cart_repo.get_by_id(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        menu_item = await self.menu_repo.get_by_id(menu_item_id)
        if Util.is_null(menu_item):
            raise ValueError("Menu item not found")

        if not menu_item.available:
            raise ValueError("Menu item is not available")

        existing_item = await self.cart_item_repo.get_by_cart_and_item(cart_id, menu_item_id)

        if Util.is_not_null(existing_item) and existing_item.notes == notes:
            new_quantity = existing_item.quantity + quantity
            await self.cart_item_repo.update(existing_item.id, {
                "quantity": new_quantity,
                "total_price": float(menu_item.price) * new_quantity
            })
        else:
            cart_item = CartItemModel(
                cart_id=cart_id,
                item_id=menu_item_id,
                item_name=menu_item.name,
                quantity=quantity,
                unit_price=menu_item.price,
                total_price=float(menu_item.price) * quantity,
                notes=notes,
                status=CartItemStatus.DRAFT
            )
            await self.cart_item_repo.create(cart_item)

        return await self._update_cart_totals(cart_id)

    async def update_item_quantity(
        self,
        cart_id: str,
        cart_item_id: str,
        quantity: int
    ) -> Dict[str, Any]:
        cart = await self.cart_repo.get_by_id(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        if quantity <= 0:
            await self.cart_item_repo.delete(cart_item_id)
        else:
            await self.cart_item_repo.update_quantity(cart_item_id, quantity)

        return await self._update_cart_totals(cart_id)

    async def remove_item(self, cart_id: str, cart_item_id: str) -> Dict[str, Any]:
        await self.cart_item_repo.delete(cart_item_id)
        return await self._update_cart_totals(cart_id)

    async def clear_cart(self, cart_id: str) -> bool:
        items = await self.cart_item_repo.get_by_cart(cart_id)
        for item in items:
            await self.cart_item_repo.delete(item.id)
        await self._update_cart_totals(cart_id)
        return True

    async def get_cart(self, cart_id: str) -> Optional[Dict[str, Any]]:
        cart = await self.cart_repo.get_with_items(cart_id)
        if Util.is_null(cart):
            return None
        return self._cart_to_dict(cart)

    async def get_cart_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        cart = await self.cart_repo.get_by_session_with_items(session_id)
        if Util.is_null(cart):
            return None
        return self._cart_to_dict(cart)

    async def submit_order(
        self,
        cart_id: str,
        user_id: str,
        customer_name: str = None,
        customer_phone: str = None,
        resource_id: str = None
    ) -> Dict[str, Any]:
        """Customer submits order - goes to PENDING_APPROVAL status"""
        cart = await self.cart_repo.get_with_items(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        if not cart.items:
            raise ValueError("Cart is empty")

        update_data = {
            "status": CartStatus.PENDING_APPROVAL,
            "user_id": user_id
        }
        if customer_name:
            update_data["customer_name"] = customer_name
        if customer_phone:
            update_data["customer_phone"] = customer_phone
        if resource_id:
            update_data["resource_id"] = resource_id

        await self.cart_repo.update(cart_id, update_data)

        cart = await self.cart_repo.get_with_items(cart_id)
        cart_data = self._cart_to_dict(cart)

        await connection_manager.broadcast_order_update(cart_data)
        await event_bus.publish(EventType.ORDER_CREATED, cart_data)

        return cart_data

    async def approve_order(
        self,
        cart_id: str,
        estimated_ready_time: int = None
    ) -> Dict[str, Any]:
        """Admin approves order - goes to CONFIRMED status"""
        cart = await self.cart_repo.get_with_items(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        if cart.status != CartStatus.PENDING_APPROVAL:
            raise ValueError(f"Order cannot be approved (current status: {cart.status.value})")

        update_data = {
            "status": CartStatus.CONFIRMED
        }
        if estimated_ready_time:
            update_data["estimated_ready_time"] = estimated_ready_time

        await self.cart_repo.update(cart_id, update_data)
        await self.cart_item_repo.update_all_status_by_cart(cart_id, CartItemStatus.DRAFT, CartItemStatus.PENDING)

        cart = await self.cart_repo.get_with_items(cart_id)
        cart_data = self._cart_to_dict(cart)

        await connection_manager.broadcast_order_update(cart_data)
        await event_bus.publish(EventType.ORDER_STATUS_CHANGED, cart_data)

        return cart_data

    async def reject_order(
        self,
        cart_id: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """Admin rejects order - goes to CANCELLED status"""
        cart = await self.cart_repo.get_with_items(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        if cart.status != CartStatus.PENDING_APPROVAL:
            raise ValueError(f"Order cannot be rejected (current status: {cart.status.value})")

        update_data = {
            "status": CartStatus.CANCELLED,
            "notes": reason or "Rejected by admin"
        }

        await self.cart_repo.update(cart_id, update_data)

        cart = await self.cart_repo.get_with_items(cart_id)
        cart_data = self._cart_to_dict(cart)

        await connection_manager.broadcast_order_update(cart_data)

        return cart_data

    async def confirm_order(
        self,
        cart_id: str,
        customer_name: str = None,
        customer_phone: str = None,
        resource_id: str = None,
        estimated_ready_time: int = None
    ) -> Dict[str, Any]:
        """Legacy method - directly confirms (for businesses that don't require approval)"""
        cart = await self.cart_repo.get_with_items(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        if not cart.items:
            raise ValueError("Cart is empty")

        update_data = {
            "status": CartStatus.CONFIRMED
        }
        if customer_name:
            update_data["customer_name"] = customer_name
        if customer_phone:
            update_data["customer_phone"] = customer_phone
        if resource_id:
            update_data["resource_id"] = resource_id
        if estimated_ready_time:
            update_data["estimated_ready_time"] = estimated_ready_time

        await self.cart_repo.update(cart_id, update_data)
        await self.cart_item_repo.update_all_status_by_cart(cart_id, CartItemStatus.DRAFT, CartItemStatus.PENDING)

        cart = await self.cart_repo.get_with_items(cart_id)
        cart_data = self._cart_to_dict(cart)

        await connection_manager.broadcast_order_update(cart_data)
        await event_bus.publish(EventType.ORDER_CREATED, cart_data)

        return cart_data

    async def update_cart_status(self, cart_id: str, status: CartStatus) -> Optional[Dict[str, Any]]:
        cart = await self.cart_repo.update_status(cart_id, status)
        if Util.is_null(cart):
            return None

        cart = await self.cart_repo.get_with_items(cart_id)
        cart_data = self._cart_to_dict(cart)

        await connection_manager.broadcast_order_update(cart_data)
        await event_bus.publish(EventType.ORDER_STATUS_CHANGED, cart_data)

        return cart_data

    async def update_item_status(
        self,
        cart_item_id: str,
        status: CartItemStatus,
        prepared_by: str = None
    ) -> Optional[Dict[str, Any]]:
        item = await self.cart_item_repo.update_status(cart_item_id, status, prepared_by)
        if Util.is_null(item):
            return None

        cart = await self.cart_repo.get_with_items(item.cart_id)
        return self._cart_to_dict(cart)

    async def get_pending_orders(self, business_id: str) -> List[Dict[str, Any]]:
        carts = await self.cart_repo.get_pending_orders(business_id)
        return [self._cart_to_dict(cart) for cart in carts]

    async def get_orders_by_status(self, business_id: str, status: CartStatus) -> List[Dict[str, Any]]:
        carts = await self.cart_repo.get_by_status(business_id, status)
        return [self._cart_to_dict(cart) for cart in carts]

    async def _update_cart_totals(self, cart_id: str) -> Dict[str, Any]:
        items = await self.cart_item_repo.get_by_cart(cart_id)

        item_count = sum(item.quantity for item in items)
        subtotal = Decimal(sum(float(item.total_price) for item in items))
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        await self.cart_repo.update_totals(cart_id, item_count, subtotal, tax, total)

        cart = await self.cart_repo.get_with_items(cart_id)
        return self._cart_to_dict(cart)

    def _cart_to_dict(self, cart: CartModel) -> Dict[str, Any]:
        return {
            "id": cart.id,
            "session_id": cart.session_id,
            "device_id": cart.device_id,
            "user_id": cart.user_id,
            "business_id": cart.business_id,
            "resource_id": cart.resource_id,
            "customer_name": cart.customer_name,
            "customer_phone": cart.customer_phone,
            "intent": cart.intent.value if cart.intent else None,
            "item_count": cart.item_count,
            "subtotal": float(cart.subtotal),
            "tax": float(cart.tax),
            "total": float(cart.total),
            "status": cart.status.value if cart.status else None,
            "source": cart.source.value if cart.source else None,
            "notes": cart.notes,
            "estimated_ready_time": cart.estimated_ready_time,
            "items": [self._item_to_dict(item) for item in (cart.items or [])],
            "created_at": cart.created_at.isoformat() if cart.created_at else None
        }

    def _item_to_dict(self, item: CartItemModel) -> Dict[str, Any]:
        return {
            "id": item.id,
            "item_id": item.item_id,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "total_price": float(item.total_price),
            "notes": item.notes,
            "status": item.status.value if item.status else None,
            "prepared_by": item.prepared_by
        }
