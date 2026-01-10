from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session
from app.services.menu_service import MenuService
from app.api.v1.schemas import CategoryCreate, MenuItemCreate, MenuItemUpdate, ApiResponse
from app.utils.null_check import Util

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("")
async def get_menu(session: AsyncSession = Depends(get_db_session)):
    service = MenuService(session)
    menu = await service.get_full_menu()
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
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    items = await service.search_menu_items(q)
    return ApiResponse(success=True, data=items)


@router.post("/categories")
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    category = await service.create_category(
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
        name=data.name,
        price=data.price,
        category_id=data.category_id,
        description=data.description,
        image_url=data.image_url,
        preparation_time_mins=data.preparation_time_mins,
        tags=data.tags,
        customizations=data.customizations
    )
    return ApiResponse(success=True, data={"id": item.id, "name": item.name})


@router.patch("/items/{item_id}/availability")
async def update_item_availability(
    item_id: str,
    is_available: bool,
    session: AsyncSession = Depends(get_db_session)
):
    service = MenuService(session)
    item = await service.update_item_availability(item_id, is_available)
    if Util.is_null(item):
        raise HTTPException(status_code=404, detail="Menu item not found")
    return ApiResponse(success=True, message="Availability updated")

