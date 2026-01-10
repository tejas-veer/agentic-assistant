from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.cart_service import CartService
from app.api.v1.schemas import CartItemAdd, CartItemUpdate, ApiResponse
from app.utils.null_check import Util

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/{session_id}")
async def get_cart(
    session_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    cart = await service.get_cart(session_id)
    return ApiResponse(success=True, data=cart)


@router.post("/{session_id}/items")
async def add_to_cart(
    session_id: str,
    device_id: str,
    data: CartItemAdd,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.add_item(
            session_id=session_id,
            device_id=device_id,
            menu_item_id=data.menu_item_id,
            quantity=data.quantity,
            customizations=data.customizations,
            special_instructions=data.special_instructions
        )
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{session_id}/items")
async def update_cart_item(
    session_id: str,
    data: CartItemUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.update_item_quantity(
            session_id=session_id,
            menu_item_id=data.menu_item_id,
            quantity=data.quantity
        )
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{session_id}/items/{menu_item_id}")
async def remove_from_cart(
    session_id: str,
    menu_item_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    try:
        cart = await service.remove_item(session_id, menu_item_id)
        return ApiResponse(success=True, data=cart)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{session_id}")
async def clear_cart(
    session_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = CartService(session)
    await service.clear_cart(session_id)
    return ApiResponse(success=True, message="Cart cleared")

