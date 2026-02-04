from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from .base_repository import BaseRepository
from ..models import BillModel, BillItemModel
from app.domain.shared.enums import BillStatus, BillItemStatus


class BillRepository(BaseRepository[BillModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BillModel)

    async def get_by_cart(self, cart_id: str) -> Optional[BillModel]:
        result = await self.session.execute(
            select(BillModel)
            .where(BillModel.cart_id == cart_id, BillModel.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_with_items(self, bill_id: str) -> Optional[BillModel]:
        result = await self.session.execute(
            select(BillModel)
            .where(BillModel.id == bill_id, BillModel.is_active == True)
            .options(selectinload(BillModel.items))
        )
        return result.scalar_one_or_none()

    async def get_by_business(self, business_id: str, limit: int = 50) -> List[BillModel]:
        result = await self.session.execute(
            select(BillModel)
            .where(BillModel.business_id == business_id, BillModel.is_active == True)
            .order_by(BillModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(self, business_id: str, status: BillStatus, limit: int = 50) -> List[BillModel]:
        result = await self.session.execute(
            select(BillModel)
            .where(
                BillModel.business_id == business_id,
                BillModel.status == status,
                BillModel.is_active == True
            )
            .order_by(BillModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(self, bill_id: str, status: BillStatus) -> Optional[BillModel]:
        return await self.update(bill_id, {"status": status, "updated_at": datetime.utcnow()})

    async def add_payment(self, bill_id: str, amount, payment_mode, payment_ref: str = None) -> Optional[BillModel]:
        bill = await self.get_by_id(bill_id)
        if bill:
            new_paid = float(bill.paid_amount) + float(amount)
            new_status = BillStatus.PAID if new_paid >= float(bill.total_amount) else BillStatus.PARTIAL
            return await self.update(bill_id, {
                "paid_amount": new_paid,
                "payment_mode": payment_mode,
                "payment_ref": payment_ref,
                "status": new_status,
                "updated_at": datetime.utcnow()
            })
        return None


class BillItemRepository(BaseRepository[BillItemModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BillItemModel)

    async def get_by_bill(self, bill_id: str) -> List[BillItemModel]:
        result = await self.session.execute(
            select(BillItemModel)
            .where(BillItemModel.bill_id == bill_id, BillItemModel.is_active == True)
        )
        return list(result.scalars().all())

    async def get_unpaid_by_bill(self, bill_id: str) -> List[BillItemModel]:
        result = await self.session.execute(
            select(BillItemModel)
            .where(
                BillItemModel.bill_id == bill_id,
                BillItemModel.status == BillItemStatus.UNPAID,
                BillItemModel.is_active == True
            )
        )
        return list(result.scalars().all())

    async def mark_as_paid(self, bill_item_id: str, paid_by_user_id: str = None) -> Optional[BillItemModel]:
        data = {"status": BillItemStatus.PAID, "updated_at": datetime.utcnow()}
        if paid_by_user_id:
            data["paid_by_user_id"] = paid_by_user_id
        return await self.update(bill_item_id, data)
