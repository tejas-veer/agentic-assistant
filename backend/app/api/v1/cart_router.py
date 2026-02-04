from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.infrastructure.database.connection import get_db_session
from app.services.cart_service import CartService
from app.api.v1.schemas import (
    CartCreate, CartItemAdd, CartItemUpdate, CartConfirm,
    CartStatusUpdate, CartItemStatusUpdate, ApiResponse
)
from app.domain.shared.enums import CartStatus
from app.utils.null_check import Util

router = APIRouter(prefix="/cart", tags=["Cart"])


def serialize_cart_item_dict(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "cartId": item.get("cart_id"),
        "itemId": item.get("item_id"),
        "itemName": item.get("item_name"),
        "quantity": item.get("quantity", 0),
        "unitPrice": item.get("unit_price", 0),
        "totalPrice": item.get("total_price", 0),
        "notes": item.get("notes"),
        "status": item.get("status"),
        "preparedBy": item.get("prepared_by"),
        "isActive": item.get("is_active", True),
        "createdAt": item.get("created_at"),
        "updatedAt": item.get("updated_at"),
    }


def serialize_cart_dict(cart: Optional[dict]) -> Optional[dict]:
    if Util.is_null(cart):
        return None
    data = {
        "id": cart.get("id"),
        "sessionId": cart.get("session_id"),
        "deviceId": cart.get("device_id"),
        "userId": cart.get("user_id"),
        "businessId": cart.get("business_id"),
        "intent": cart.get("intent"),
        "resourceId": cart.get("resource_id"),
        "customerName": cart.get("customer_name"),
        "customerPhone": cart.get("customer_phone"),
        "itemCount": cart.get("item_count", 0),
        "subtotal": cart.get("subtotal", 0),
        "tax": cart.get("tax", 0),
        "total": cart.get("total", 0),
        "status": cart.get("status"),
        "source": cart.get("source"),
        "notes": cart.get("notes"),
        "estimatedReadyTime": cart.get("estimated_ready_time"),
        "assistantSessionId": cart.get("assistant_session_id"),
        "isActive": cart.get("is_active", True),
        "createdAt": cart.get("created_at"),
        "updatedAt": cart.get("updated_at"),
    }
    items = cart.get("items", [])
    if items:
        data["items"] = [serialize_cart_item_dict(item) for item in items]
    return data


def serialize_carts_dict(carts: List[dict]) -> List[dict]:
    return [serialize_cart_dict(cart) for cart in carts if cart]


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
    return ApiResponse(success=True, data={"id": cart.id, "sessionId": cart.session_id})


@router.get("/{cart_id}")
async def get_cart(
    cart_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.get_cart(cart_id)
    return ApiResponse(success=True, data=serialize_cart_dict(cart))


@router.get("/session/{session_id}")
async def get_cart_by_session(
    session_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.get_cart_by_session(session_id)
    return ApiResponse(success=True, data=serialize_cart_dict(cart))


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
        return ApiResponse(success=True, data=serialize_cart_dict(cart))
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
        return ApiResponse(success=True, data=serialize_cart_dict(cart))
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
        return ApiResponse(success=True, data=serialize_cart_dict(cart))
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


@router.post("/{cart_id}/submit")
async def submit_order(
    cart_id: str,
    data: CartConfirm,
    session: AsyncSession = Depends(get_db_session)
):
    """Customer submits order for approval"""
    service = CartService(session)
    try:
        cart = await service.submit_order(
            cart_id=cart_id,
            user_id=data.user_id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            resource_id=data.resource_id
        )
        return ApiResponse(success=True, data=serialize_cart_dict(cart), message="Order submitted for approval")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{cart_id}/approve")
async def approve_order(
    cart_id: str,
    estimated_ready_time: Optional[int] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Admin approves order"""
    service = CartService(session)
    try:
        cart = await service.approve_order(
            cart_id=cart_id,
            estimated_ready_time=estimated_ready_time
        )
        return ApiResponse(success=True, data=serialize_cart_dict(cart), message="Order approved")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{cart_id}/reject")
async def reject_order(
    cart_id: str,
    reason: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Admin rejects order"""
    service = CartService(session)
    try:
        cart = await service.reject_order(
            cart_id=cart_id,
            reason=reason
        )
        return ApiResponse(success=True, data=serialize_cart_dict(cart), message="Order rejected")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{cart_id}/confirm")
async def confirm_order(
    cart_id: str,
    data: CartConfirm,
    session: AsyncSession = Depends(get_db_session)
):
    """Direct confirm (for businesses without approval requirement)"""
    service = CartService(session)
    try:
        cart = await service.confirm_order(
            cart_id=cart_id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            resource_id=data.resource_id,
            estimated_ready_time=data.estimated_ready_time
        )
        return ApiResponse(success=True, data=serialize_cart_dict(cart))
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
    return ApiResponse(success=True, data=serialize_cart_dict(cart))


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
    return ApiResponse(success=True, data=serialize_cart_dict(cart))


@router.get("/business/{business_id}/pending")
async def get_pending_orders(
    business_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get orders that are confirmed and in progress (for kitchen)"""
    service = CartService(session)
    orders = await service.get_pending_orders(business_id)
    return ApiResponse(success=True, data=serialize_carts_dict(orders))


@router.get("/business/{business_id}/pending-approval")
async def get_orders_pending_approval(
    business_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get orders awaiting admin approval"""
    service = CartService(session)
    orders = await service.get_orders_by_status(business_id, CartStatus.PENDING_APPROVAL)
    return ApiResponse(success=True, data=serialize_carts_dict(orders))


@router.get("/business/{business_id}/status/{status}")
async def get_orders_by_status(
    business_id: str,
    status: CartStatus,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    orders = await service.get_orders_by_status(business_id, status)
    return ApiResponse(success=True, data=serialize_carts_dict(orders))
