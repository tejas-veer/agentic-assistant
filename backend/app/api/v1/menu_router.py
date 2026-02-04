from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.menu_service import MenuService
from app.api.v1.schemas import CategoryCreate, MenuItemCreate, MenuItemUpdate, ApiResponse
from app.utils.null_check import Util

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("")
async def get_menu(
    business_id: str = Query("1", description="Business ID"),
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    menu = await service.get_full_menu(business_id)
    return ApiResponse(success=True, data=menu)


@router.get("/items/{item_id}")
async def get_menu_item(
    item_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    item = await service.get_item_by_id(item_id)
    if Util.is_null(item):
        raise HTTPException(status_code=404, detail="Menu item not found")
    return ApiResponse(success=True, data=item)


@router.get("/search")
async def search_menu(
    q: str,
    business_id: str = Query("1", description="Business ID"),
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    items = await service.search_menu_items(business_id, q)
    return ApiResponse(success=True, data=items)


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
