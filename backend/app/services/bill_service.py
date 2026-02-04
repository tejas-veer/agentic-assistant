from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.infrastructure.database.repositories import BillRepository, BillItemRepository, CartRepository, CartItemRepository
from app.infrastructure.database.repositories.business_repository import ResourceRepository
from app.infrastructure.database.models import BillModel, BillItemModel
from app.domain.shared.enums import BillStatus, BillItemStatus, CartStatus, PaymentMethod, ResourceStatus
from app.utils.null_check import Util


class BillService:
    def __init__(self, session: AsyncSession):
        self.bill_repo = BillRepository(session)
        self.bill_item_repo = BillItemRepository(session)
        self.cart_repo = CartRepository(session)
        self.cart_item_repo = CartItemRepository(session)
        self.resource_repo = ResourceRepository(session)
        self.session = session

    async def create_bill_from_cart(
        self,
        cart_id: str,
        tax_percent: Decimal = Decimal("5.0"),
        discount_amount: Decimal = Decimal("0"),
        service_charge: Decimal = Decimal("0")
    ) -> Dict[str, Any]:
        cart = await self.cart_repo.get_with_items(cart_id)
        if Util.is_null(cart):
            raise ValueError("Cart not found")

        if not cart.items:
            raise ValueError("Cart has no items")

        existing_bill = await self.bill_repo.get_by_cart(cart_id)
        if Util.is_not_null(existing_bill):
            raise ValueError("Bill already exists for this cart")

        subtotal = Decimal(sum(float(item.total_price) for item in cart.items))
        tax_amount = subtotal * (tax_percent / Decimal("100"))
        total_amount = subtotal + tax_amount - discount_amount + service_charge

        bill = BillModel(
            cart_id=cart_id,
            business_id=cart.business_id,
            subtotal=subtotal,
            tax_percent=tax_percent,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            service_charge=service_charge,
            total_amount=total_amount,
            paid_amount=Decimal("0"),
            status=BillStatus.PENDING
        )
        bill = await self.bill_repo.create(bill)

        for cart_item in cart.items:
            bill_item = BillItemModel(
                bill_id=bill.id,
                cart_item_id=cart_item.id,
                item_name=cart_item.item_name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                status=BillItemStatus.UNPAID
            )
            await self.bill_item_repo.create(bill_item)

        return await self.get_bill(bill.id)

    async def get_bill(self, bill_id: str) -> Optional[Dict[str, Any]]:
        bill = await self.bill_repo.get_with_items(bill_id)
        if Util.is_null(bill):
            return None
        return self._bill_to_dict(bill)

    async def get_bill_by_cart(self, cart_id: str) -> Optional[Dict[str, Any]]:
        bill = await self.bill_repo.get_by_cart(cart_id)
        if Util.is_null(bill):
            return None
        bill = await self.bill_repo.get_with_items(bill.id)
        return self._bill_to_dict(bill)

    async def process_payment(
        self,
        bill_id: str,
        amount: Decimal,
        payment_mode: PaymentMethod,
        payment_ref: str = None
    ) -> Dict[str, Any]:
        bill = await self.bill_repo.get_by_id(bill_id)
        if Util.is_null(bill):
            raise ValueError("Bill not found")

        bill = await self.bill_repo.add_payment(bill_id, amount, payment_mode, payment_ref)

        if bill.status == BillStatus.PAID:
            items = await self.bill_item_repo.get_by_bill(bill_id)
            for item in items:
                await self.bill_item_repo.mark_as_paid(item.id)

            await self.cart_repo.update_status(bill.cart_id, CartStatus.COMPLETED)
            
            # Free the resource when bill is fully paid
            cart = await self.cart_repo.get_by_id(bill.cart_id)
            if Util.is_not_null(cart) and Util.is_not_null(cart.resource_id):
                await self.resource_repo.update_status(cart.resource_id, ResourceStatus.AVAILABLE)

        return await self.get_bill(bill_id)

    async def process_split_payment(
        self,
        bill_id: str,
        bill_item_ids: List[str],
        paid_by_user_id: str,
        amount: Decimal,
        payment_mode: PaymentMethod
    ) -> Dict[str, Any]:
        bill = await self.bill_repo.get_by_id(bill_id)
        if Util.is_null(bill):
            raise ValueError("Bill not found")

        for item_id in bill_item_ids:
            await self.bill_item_repo.mark_as_paid(item_id, paid_by_user_id)

        bill = await self.bill_repo.add_payment(bill_id, amount, payment_mode)

        if bill.status == BillStatus.PAID:
            await self.cart_repo.update_status(bill.cart_id, CartStatus.COMPLETED)

        return await self.get_bill(bill_id)

    async def get_bills_by_business(self, business_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        bills = await self.bill_repo.get_by_business(business_id, limit)
        result = []
        for bill in bills:
            bill_with_items = await self.bill_repo.get_with_items(bill.id)
            result.append(self._bill_to_dict(bill_with_items))
        return result

    async def get_bills_by_status(self, business_id: str, status: BillStatus, limit: int = 50) -> List[Dict[str, Any]]:
        bills = await self.bill_repo.get_by_status(business_id, status, limit)
        result = []
        for bill in bills:
            bill_with_items = await self.bill_repo.get_with_items(bill.id)
            result.append(self._bill_to_dict(bill_with_items))
        return result

    def _bill_to_dict(self, bill: BillModel) -> Dict[str, Any]:
        return {
            "id": bill.id,
            "cart_id": bill.cart_id,
            "business_id": bill.business_id,
            "subtotal": float(bill.subtotal),
            "tax_percent": float(bill.tax_percent),
            "tax_amount": float(bill.tax_amount),
            "discount_amount": float(bill.discount_amount),
            "service_charge": float(bill.service_charge),
            "total_amount": float(bill.total_amount),
            "paid_amount": float(bill.paid_amount),
            "balance_due": float(bill.total_amount) - float(bill.paid_amount),
            "payment_mode": bill.payment_mode.value if bill.payment_mode else None,
            "status": bill.status.value if bill.status else None,
            "payment_ref": bill.payment_ref,
            "items": [self._bill_item_to_dict(item) for item in (bill.items or [])],
            "created_at": bill.created_at.isoformat() if bill.created_at else None
        }

    def _bill_item_to_dict(self, item: BillItemModel) -> Dict[str, Any]:
        return {
            "id": item.id,
            "cart_item_id": item.cart_item_id,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "total_price": float(item.total_price),
            "paid_by_user_id": item.paid_by_user_id,
            "status": item.status.value if item.status else None
        }
