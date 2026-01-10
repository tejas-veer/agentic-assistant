from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from .base_repository import BaseRepository
from ..models import OrderModel, CartModel
from app.domain.shared.enums import OrderStatus


class OrderRepository(BaseRepository[OrderModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OrderModel)
    
    async def get_by_order_number(self, order_number: str) -> Optional[OrderModel]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.order_number == order_number)
        )
        return result.scalar_one_or_none()
    
    async def get_by_status(self, status: OrderStatus, limit: int = 50) -> List[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.status == status, OrderModel.is_active == True)
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_pending_orders(self) -> List[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .where(
                OrderModel.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING]),
                OrderModel.is_active == True
            )
            .order_by(OrderModel.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_orders_by_device(self, device_id: str, limit: int = 20) -> List[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.device_id == device_id, OrderModel.is_active == True)
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_status(self, order_id: str, status: OrderStatus) -> Optional[OrderModel]:
        return await self.update(order_id, {"status": status, "updated_at": datetime.utcnow()})
    
    async def get_today_orders_count(self) -> int:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count(OrderModel.id))
            .where(OrderModel.created_at >= today_start)
        )
        return result.scalar() or 0
    
    async def generate_order_number(self) -> str:
        count = await self.get_today_orders_count()
        today = datetime.utcnow().strftime("%Y%m%d")
        return f"ORD-{today}-{count + 1:04d}"


class CartRepository(BaseRepository[CartModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CartModel)
    
    async def get_by_session(self, session_id: str) -> Optional[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.session_id == session_id, CartModel.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def clear_cart(self, session_id: str) -> bool:
        cart = await self.get_by_session(session_id)
        if cart:
            return await self.delete(cart.id)
        return False

