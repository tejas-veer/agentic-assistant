from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from .base_repository import BaseRepository
from ..models import CartModel, CartItemModel
from app.domain.shared.enums import CartStatus, CartItemStatus


class CartRepository(BaseRepository[CartModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CartModel)

    async def get_by_session(self, session_id: str) -> Optional[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.session_id == session_id, CartModel.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_session_with_items(self, session_id: str) -> Optional[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.session_id == session_id, CartModel.is_active == True)
            .options(selectinload(CartModel.items))
        )
        return result.scalar_one_or_none()

    async def get_with_items(self, cart_id: str) -> Optional[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.id == cart_id, CartModel.is_active == True)
            .options(selectinload(CartModel.items))
        )
        return result.scalar_one_or_none()

    async def get_by_business(self, business_id: str, limit: int = 50) -> List[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.business_id == business_id, CartModel.is_active == True)
            .order_by(CartModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(self, business_id: str, status: CartStatus, limit: int = 50) -> List[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(
                CartModel.business_id == business_id,
                CartModel.status == status,
                CartModel.is_active == True
            )
            .options(selectinload(CartModel.items))
            .order_by(CartModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_orders(self, business_id: str) -> List[CartModel]:
        result = await self.session.execute(
            select(CartModel)
            .where(
                CartModel.business_id == business_id,
                CartModel.status.in_([CartStatus.CONFIRMED, CartStatus.IN_PROGRESS]),
                CartModel.is_active == True
            )
            .options(selectinload(CartModel.items))
            .order_by(CartModel.created_at.asc())
        )
        return list(result.scalars().all())

    async def update_status(self, cart_id: str, status: CartStatus) -> Optional[CartModel]:
        return await self.update(cart_id, {"status": status, "updated_at": datetime.utcnow()})

    async def update_totals(self, cart_id: str, item_count: int, subtotal, tax, total) -> Optional[CartModel]:
        return await self.update(cart_id, {
            "item_count": item_count,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "updated_at": datetime.utcnow()
        })


class CartItemRepository(BaseRepository[CartItemModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CartItemModel)

    async def get_by_cart(self, cart_id: str) -> List[CartItemModel]:
        result = await self.session.execute(
            select(CartItemModel)
            .where(CartItemModel.cart_id == cart_id, CartItemModel.is_active == True)
            .order_by(CartItemModel.created_at)
        )
        return list(result.scalars().all())

    async def get_by_cart_and_item(self, cart_id: str, item_id: str) -> Optional[CartItemModel]:
        result = await self.session.execute(
            select(CartItemModel)
            .where(
                CartItemModel.cart_id == cart_id,
                CartItemModel.item_id == item_id,
                CartItemModel.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def update_status(self, cart_item_id: str, status: CartItemStatus, prepared_by: str = None) -> Optional[CartItemModel]:
        data = {"status": status, "updated_at": datetime.utcnow()}
        if prepared_by:
            data["prepared_by"] = prepared_by
        return await self.update(cart_item_id, data)

    async def update_quantity(self, cart_item_id: str, quantity: int) -> Optional[CartItemModel]:
        item = await self.get_by_id(cart_item_id)
        if item:
            total_price = float(item.unit_price) * quantity
            return await self.update(cart_item_id, {
                "quantity": quantity,
                "total_price": total_price,
                "updated_at": datetime.utcnow()
            })
        return None

    async def update_all_status_by_cart(self, cart_id: str, old_status: CartItemStatus, new_status: CartItemStatus):
        items = await self.get_by_cart(cart_id)
        for item in items:
            if item.status == old_status:
                await self.update_status(item.id, new_status)
