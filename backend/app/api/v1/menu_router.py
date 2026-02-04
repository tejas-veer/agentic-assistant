from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from app.infrastructure.database.connection import get_db_session
from app.services.menu_service import MenuService
from app.api.v1.schemas import (
    CategoryCreate, MenuItemCreate, MenuItemUpdate, ApiResponse,
    CategoryResponse, MenuItemResponse
)
from app.utils.null_check import Util
from app.core.constants import DEFAULT_BUSINESS_ID

router = APIRouter(prefix="/menu", tags=["Menu"])


def serialize_menu_item_dict(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "businessId": item.get("business_id"),
        "categoryId": item.get("category_id"),
        "name": item.get("name"),
        "description": item.get("description"),
        "price": item.get("price"),
        "imageUrl": item.get("image_url"),
        "available": item.get("available", True),
        "quantity": item.get("quantity", 0),
        "preparationTimeMins": item.get("preparation_time_mins", 10),
        "displayOrder": item.get("display_order", 0),
        "isActive": item.get("is_active", True),
    }


def serialize_category_dict(category: dict) -> dict:
    data = {
        "id": category.get("id"),
        "businessId": category.get("business_id"),
        "name": category.get("name"),
        "description": category.get("description"),
        "imageUrl": category.get("image_url"),
        "displayOrder": category.get("display_order", 0),
        "isActive": category.get("is_active", True),
    }
    items = category.get("items", [])
    if items:
        data["items"] = [serialize_menu_item_dict(item) for item in items]
    return data


def serialize_menu_item_model(item) -> dict:
    return {
        "id": item.id,
        "businessId": item.business_id,
        "categoryId": item.category_id,
        "name": item.name,
        "description": item.description,
        "price": float(item.price) if item.price else 0,
        "imageUrl": item.image_url,
        "available": item.available,
        "quantity": item.quantity,
        "preparationTimeMins": item.preparation_time_mins,
        "displayOrder": item.display_order,
        "isActive": item.is_active,
        "createdAt": item.created_at.isoformat() if item.created_at else None,
        "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
    }


@router.get("")
async def get_menu(
    business_id: str = Query(DEFAULT_BUSINESS_ID, description="Business ID"),
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    categories = await service.get_full_menu(business_id)
    data = [serialize_category_dict(cat) for cat in categories]
    return ApiResponse(success=True, data=data)


@router.get("/items/{item_id}")
async def get_menu_item(
    item_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    item = await service.get_item_by_id(item_id)
    if Util.is_null(item):
        raise HTTPException(status_code=404, detail="Menu item not found")
    return ApiResponse(success=True, data=serialize_menu_item_dict(item))


@router.get("/search")
async def search_menu(
    q: str,
    business_id: str = Query(DEFAULT_BUSINESS_ID, description="Business ID"),
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    items = await service.search_menu_items(business_id, q)
    data = [serialize_menu_item_dict(item) for item in items]
    return ApiResponse(success=True, data=data)


@router.post("/categories")
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    category = await service.create_category(
        business_id=data.business_id,
        name=data.name,
        description=data.description,
        image_url=data.image_url
    )
    return ApiResponse(success=True, data={"id": category.id, "name": category.name})


@router.post("/items")
async def create_menu_item(
    data: MenuItemCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    item = await service.create_menu_item(
        business_id=data.business_id,
        category_id=data.category_id,
        name=data.name,
        price=data.price,
        description=data.description,
        image_url=data.image_url,
        preparation_time_mins=data.preparation_time_mins,
        quantity=data.quantity
    )
    return ApiResponse(success=True, data={"id": item.id, "name": item.name})


@router.patch("/items/{item_id}/availability")
async def update_item_availability(
    item_id: str,
    available: bool,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    item = await service.update_item_availability(item_id, available)
    if Util.is_null(item):
        raise HTTPException(status_code=404, detail="Menu item not found")
    return ApiResponse(success=True, message="Availability updated")
