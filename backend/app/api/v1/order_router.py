from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.order_service import OrderService
from app.api.v1.schemas import OrderCreate, OrderStatusUpdate, OrderConfirm, PaymentUpdate, ApiResponse
from app.domain.shared.enums import OrderStatus
from app.utils.null_check import Util

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("")
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    try:
        order = await service.create_order_from_cart(
            session_id=data.session_id,
            table_number=data.table_number,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            payment_method=data.payment_method,
            notes=data.notes
        )
        return ApiResponse(success=True, data=order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pending")
async def get_pending_orders(
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    orders = await service.get_pending_orders()
    return ApiResponse(success=True, data=orders)


@router.get("/status/{status}")
async def get_orders_by_status(
    status: OrderStatus,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    orders = await service.get_orders_by_status(status)
    return ApiResponse(success=True, data=orders)


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    order = await service.get_order(order_id)
    if Util.is_null(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return ApiResponse(success=True, data=order)


@router.get("/number/{order_number}")
async def get_order_by_number(
    order_number: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    order = await service.get_order_by_number(order_number)
    if Util.is_null(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return ApiResponse(success=True, data=order)


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    order = await service.update_order_status(order_id, data.status)
    if Util.is_null(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return ApiResponse(success=True, data=order)


@router.post("/{order_id}/confirm")
async def confirm_order(
    order_id: str,
    data: OrderConfirm,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    order = await service.confirm_order(order_id, data.estimated_ready_time)
    if Util.is_null(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return ApiResponse(success=True, data=order)


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    reason: str = None,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    order = await service.cancel_order(order_id, reason)
    if Util.is_null(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return ApiResponse(success=True, data=order)


@router.patch("/{order_id}/payment")
async def update_payment(
    order_id: str,
    data: PaymentUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = OrderService(session)
    order = await service.update_payment_status(
        order_id,
        data.payment_status,
        data.payment_method
    )
    if Util.is_null(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return ApiResponse(success=True, data=order)

