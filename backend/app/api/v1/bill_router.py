from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.bill_service import BillService
from app.api.v1.schemas import BillCreate, PaymentProcess, SplitPayment, ApiResponse
from app.domain.shared.enums import BillStatus
from app.utils.null_check import Util

router = APIRouter(prefix="/bills", tags=["Bills"])


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
        return ApiResponse(success=True, data=bill)
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
    return ApiResponse(success=True, data=bill)


@router.get("/cart/{cart_id}")
async def get_bill_by_cart(
    cart_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    bill = await service.get_bill_by_cart(cart_id)
    return ApiResponse(success=True, data=bill)


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
        return ApiResponse(success=True, data=bill)
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
        return ApiResponse(success=True, data=bill)
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
    return ApiResponse(success=True, data=bills)


@router.get("/business/{business_id}/status/{status}")
async def get_bills_by_status(
    business_id: str,
    status: BillStatus,
    limit: int = Query(50, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    service = BillService(session)
    bills = await service.get_bills_by_status(business_id, status, limit)
    return ApiResponse(success=True, data=bills)
