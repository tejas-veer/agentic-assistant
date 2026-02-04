from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.cart_service import CartService
from app.api.v1.schemas import (
    CartCreate, CartItemAdd, CartItemUpdate, CartConfirm,
    CartStatusUpdate, CartItemStatusUpdate, ApiResponse
)
from app.domain.shared.enums import CartStatus
from app.utils.null_check import Util

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("")
async def create_cart(
    data: CartCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.get_or_create_cart(
        business_id=data.business_id,
        session_id=data.session_id,
        device_id=data.device_id,
        user_id=data.user_id
    )
    return ApiResponse(success=True, data={"id": cart.id, "session_id": cart.session_id})


@router.get("/{cart_id}")
async def get_cart(
    cart_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.get_cart(cart_id)
    return ApiResponse(success=True, data=cart)


@router.get("/session/{session_id}")
async def get_cart_by_session(
    session_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.get_cart_by_session(session_id)
    return ApiResponse(success=True, data=cart)


@router.post("/{cart_id}/items")
async def add_to_cart(
    cart_id: str,
    data: CartItemAdd,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.add_item(
            cart_id=cart_id,
            menu_item_id=data.item_id,
            quantity=data.quantity,
            notes=data.notes
        )
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cart_id}/items")
async def update_cart_item(
    cart_id: str,
    data: CartItemUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.update_item_quantity(
            cart_id=cart_id,
            cart_item_id=data.cart_item_id,
            quantity=data.quantity
        )
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}/items/{cart_item_id}")
async def remove_from_cart(
    cart_id: str,
    cart_item_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.remove_item(cart_id, cart_item_id)
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}")
async def clear_cart(
    cart_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    await service.clear_cart(cart_id)
    return ApiResponse(success=True, message="Cart cleared")


@router.post("/{cart_id}/confirm")
async def confirm_order(
    cart_id: str,
    data: CartConfirm,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.confirm_order(
            cart_id=cart_id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            resource_id=data.resource_id,
            estimated_ready_time=data.estimated_ready_time
        )
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{cart_id}/status")
async def update_cart_status(
    cart_id: str,
    data: CartStatusUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.update_cart_status(cart_id, data.status)
    if Util.is_null(cart):
        raise HTTPException(status_code=404, detail="Cart not found")
    return ApiResponse(success=True, data=cart)


@router.patch("/items/{cart_item_id}/status")
async def update_item_status(
    cart_item_id: str,
    data: CartItemStatusUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.update_item_status(
        cart_item_id=cart_item_id,
        status=data.status,
        prepared_by=data.prepared_by
    )
    if Util.is_null(cart):
        raise HTTPException(status_code=404, detail="Cart item not found")
    return ApiResponse(success=True, data=cart)


@router.get("/business/{business_id}/pending")
async def get_pending_orders(
    business_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    orders = await service.get_pending_orders(business_id)
    return ApiResponse(success=True, data=orders)


@router.get("/business/{business_id}/status/{status}")
async def get_orders_by_status(
    business_id: str,
    status: CartStatus,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    orders = await service.get_orders_by_status(business_id, status)
    return ApiResponse(success=True, data=orders)
