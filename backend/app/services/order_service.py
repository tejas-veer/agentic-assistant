from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.infrastructure.database.repositories.order_repository import OrderRepository, CartRepository
from app.infrastructure.database.models import OrderModel
from app.infrastructure.messaging.websocket_manager import connection_manager
from app.infrastructure.messaging.events import event_bus, EventType
from app.domain.shared.enums import OrderStatus, PaymentStatus, PaymentMethod
from app.utils.null_check import Util


class OrderService:
    def __init__(self, session: AsyncSession):
        self.order_repo = OrderRepository(session)
        self.cart_repo = CartRepository(session)
        self.session = session
    
    async def create_order_from_cart(
        self,
        session_id: str,
        table_number: str = None,
        customer_name: str = None,
        customer_phone: str = None,
        payment_method: PaymentMethod = None,
        notes: str = None,
        assistant_session_id: str = None
    ) -> Dict[str, Any]:
        cart = await self.cart_repo.get_by_session(session_id)
        if Util.is_null(cart) or Util.is_empty(cart.items):
            raise ValueError("Cart is empty")
        
        order_number = await self.order_repo.generate_order_number()
        
        order = OrderModel(
            order_number=order_number,
            device_id=cart.device_id,
            table_number=table_number,
            customer_name=customer_name,
            customer_phone=customer_phone,
            items=cart.items,
            subtotal=cart.subtotal,
            tax=cart.tax,
            total=cart.total,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            payment_method=payment_method,
            notes=notes,
            assistant_session_id=assistant_session_id
        )
        
        order = await self.order_repo.create(order)
        await self.cart_repo.clear_cart(session_id)
        
        order_data = self._to_dict(order)
        
        await connection_manager.broadcast_order_update(order_data)
        await event_bus.publish(EventType.ORDER_CREATED, order_data)
        
        return order_data
    
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        order = await self.order_repo.get_by_id(order_id)
        if Util.is_null(order):
            return None
        return self._to_dict(order)
    
    async def get_order_by_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        order = await self.order_repo.get_by_order_number(order_number)
        if Util.is_null(order):
            return None
        return self._to_dict(order)
    
    async def get_pending_orders(self) -> List[Dict[str, Any]]:
        orders = await self.order_repo.get_pending_orders()
        return [self._to_dict(order) for order in orders]
    
    async def get_orders_by_status(self, status: OrderStatus) -> List[Dict[str, Any]]:
        orders = await self.order_repo.get_by_status(status)
        return [self._to_dict(order) for order in orders]
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Optional[Dict[str, Any]]:
        order = await self.order_repo.update_status(order_id, status)
        if Util.is_null(order):
            return None
        
        order_data = self._to_dict(order)
        
        await connection_manager.broadcast_order_update(order_data)
        await event_bus.publish(EventType.ORDER_STATUS_CHANGED, order_data)
        
        return order_data
    
    async def confirm_order(self, order_id: str, estimated_ready_time: int = None) -> Optional[Dict[str, Any]]:
        update_data = {"status": OrderStatus.CONFIRMED}
        if Util.is_not_null(estimated_ready_time):
            update_data["estimated_ready_time"] = estimated_ready_time
        
        order = await self.order_repo.update(order_id, update_data)
        if Util.is_null(order):
            return None
        
        order_data = self._to_dict(order)
        await connection_manager.broadcast_order_update(order_data)
        
        return order_data
    
    async def cancel_order(self, order_id: str, reason: str = None) -> Optional[Dict[str, Any]]:
        update_data = {"status": OrderStatus.CANCELLED}
        if Util.is_not_empty(reason):
            order = await self.order_repo.get_by_id(order_id)
            if order:
                current_notes = order.notes or ""
                update_data["notes"] = f"{current_notes}\nCancelled: {reason}".strip()
        
        order = await self.order_repo.update(order_id, update_data)
        if Util.is_null(order):
            return None
        
        order_data = self._to_dict(order)
        await connection_manager.broadcast_order_update(order_data)
        
        return order_data
    
    async def update_payment_status(
        self,
        order_id: str,
        payment_status: PaymentStatus,
        payment_method: PaymentMethod = None
    ) -> Optional[Dict[str, Any]]:
        update_data = {"payment_status": payment_status}
        if Util.is_not_null(payment_method):
            update_data["payment_method"] = payment_method
        
        order = await self.order_repo.update(order_id, update_data)
        if Util.is_null(order):
            return None
        
        return self._to_dict(order)
    
    def _to_dict(self, order: OrderModel) -> Dict[str, Any]:
        return {
            "id": order.id,
            "order_number": order.order_number,
            "device_id": order.device_id,
            "table_number": order.table_number,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "items": order.items,
            "subtotal": float(order.subtotal),
            "tax": float(order.tax),
            "discount": float(order.discount) if order.discount else 0,
            "total": float(order.total),
            "status": order.status.value if order.status else None,
            "payment_status": order.payment_status.value if order.payment_status else None,
            "payment_method": order.payment_method.value if order.payment_method else None,
            "notes": order.notes,
            "estimated_ready_time": order.estimated_ready_time,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }

