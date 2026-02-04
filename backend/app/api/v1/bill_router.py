from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.infrastructure.database.connection import get_db_session
from app.services.bill_service import BillService
from app.api.v1.schemas import BillCreate, PaymentProcess, SplitPayment, ApiResponse
from app.domain.shared.enums import BillStatus
from app.utils.null_check import Util

router = APIRouter(prefix="/bills", tags=["Bills"])


def serialize_bill_item(item) -> dict:
    return {
        "id": item.id,
        "billId": item.bill_id,
        "cartItemId": item.cart_item_id,
        "itemName": item.item_name,
        "quantity": item.quantity,
        "unitPrice": float(item.unit_price) if item.unit_price else 0,
        "totalPrice": float(item.total_price) if item.total_price else 0,
        "paidByUserId": item.paid_by_user_id,
        "status": item.status.value if item.status else None,
        "isActive": item.is_active,
        "createdAt": item.created_at.isoformat() if item.created_at else None,
        "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
    }


def serialize_bill(bill) -> Optional[dict]:
    if Util.is_null(bill):
        return None
    data = {
        "id": bill.id,
        "cartId": bill.cart_id,
        "businessId": bill.business_id,
        "subtotal": float(bill.subtotal) if bill.subtotal else 0,
        "taxPercent": float(bill.tax_percent) if bill.tax_percent else 0,
        "taxAmount": float(bill.tax_amount) if bill.tax_amount else 0,
        "discountAmount": float(bill.discount_amount) if bill.discount_amount else 0,
        "serviceCharge": float(bill.service_charge) if bill.service_charge else 0,
        "totalAmount": float(bill.total_amount) if bill.total_amount else 0,
        "paidAmount": float(bill.paid_amount) if bill.paid_amount else 0,
        "paymentMode": bill.payment_mode.value if bill.payment_mode else None,
        "status": bill.status.value if bill.status else None,
        "paymentRef": bill.payment_ref,
        "isActive": bill.is_active,
        "createdAt": bill.created_at.isoformat() if bill.created_at else None,
        "updatedAt": bill.updated_at.isoformat() if bill.updated_at else None,
    }
    if hasattr(bill, 'items') and bill.items:
        data["items"] = [serialize_bill_item(item) for item in bill.items if item.is_active]
    return data


def serialize_bills(bills) -> List[dict]:
    return [serialize_bill(bill) for bill in bills if bill]


@router.post("")
async def create_bill(
    data: BillCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    try:
        bill = await service.create_bill_from_cart(
            cart_id=data.cart_id,
            tax_percent=data.tax_percent,
            discount_amount=data.discount_amount,
            service_charge=data.service_charge
        )
        return ApiResponse(success=True, data=serialize_bill(bill))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{bill_id}")
async def get_bill(
    bill_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    bill = await service.get_bill(bill_id)
    if Util.is_null(bill):
        raise HTTPException(status_code=404, detail="Bill not found")
    return ApiResponse(success=True, data=serialize_bill(bill))


@router.get("/cart/{cart_id}")
async def get_bill_by_cart(
    cart_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    bill = await service.get_bill_by_cart(cart_id)
    return ApiResponse(success=True, data=serialize_bill(bill))


@router.post("/{bill_id}/pay")
async def process_payment(
    bill_id: str,
    data: PaymentProcess,
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    try:
        bill = await service.process_payment(
            bill_id=bill_id,
            amount=data.amount,
            payment_mode=data.payment_mode,
            payment_ref=data.payment_ref
        )
        return ApiResponse(success=True, data=serialize_bill(bill))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{bill_id}/split-pay")
async def process_split_payment(
    bill_id: str,
    data: SplitPayment,
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    try:
        bill = await service.process_split_payment(
            bill_id=bill_id,
            bill_item_ids=data.bill_item_ids,
            paid_by_user_id=data.paid_by_user_id,
            amount=data.amount,
            payment_mode=data.payment_mode
        )
        return ApiResponse(success=True, data=serialize_bill(bill))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/business/{business_id}")
async def get_bills_by_business(
    business_id: str,
    limit: int = Query(50, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    bills = await service.get_bills_by_business(business_id, limit)
    return ApiResponse(success=True, data=serialize_bills(bills))


@router.get("/business/{business_id}/status/{status}")
async def get_bills_by_status(
    business_id: str,
    status: BillStatus,
    limit: int = Query(50, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    bills = await service.get_bills_by_status(business_id, status, limit)
    return ApiResponse(success=True, data=serialize_bills(bills))
