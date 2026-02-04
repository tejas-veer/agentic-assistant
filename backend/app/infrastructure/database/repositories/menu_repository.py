from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base_repository import BaseRepository
from ..models import CategoryModel, MenuModel


class CategoryRepository(BaseRepository[CategoryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CategoryModel)

    async def get_by_business(self, business_id: str) -> List[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .where(CategoryModel.business_id == business_id, CategoryModel.is_active == True)
            .order_by(CategoryModel.display_order)
        )
        return list(result.scalars().all())

    async def get_all_with_items(self, business_id: str) -> List[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .where(CategoryModel.business_id == business_id, CategoryModel.is_active == True)
            .options(selectinload(CategoryModel.menu_items))
            .order_by(CategoryModel.display_order)
        )
        return list(result.scalars().all())


class MenuRepository(BaseRepository[MenuModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MenuModel)

    async def get_by_business(self, business_id: str) -> List[MenuModel]:
        result = await self.session.execute(
            select(MenuModel)
            .where(MenuModel.business_id == business_id, MenuModel.is_active == True)
            .order_by(MenuModel.display_order)
        )
        return list(result.scalars().all())

    async def get_by_category(self, category_id: str) -> List[MenuModel]:
        result = await self.session.execute(
            select(MenuModel)
            .where(
                MenuModel.category_id == category_id,
                MenuModel.is_active == True,
                MenuModel.available == True
            )
            .order_by(MenuModel.display_order)
        )
        return list(result.scalars().all())

    async def get_available_items(self, business_id: str) -> List[MenuModel]:
        result = await self.session.execute(
            select(MenuModel)
            .where(
                MenuModel.business_id == business_id,
                MenuModel.is_active == True,
                MenuModel.available == True
            )
            .order_by(MenuModel.display_order)
        )
        return list(result.scalars().all())

    async def search_items(self, business_id: str, query: str) -> List[MenuModel]:
        result = await self.session.execute(
            select(MenuModel)
            .where(
                MenuModel.business_id == business_id,
                MenuModel.is_active == True,
                MenuModel.available == True,
                MenuModel.name.ilike(f"%{query}%")
            )
        )
        return list(result.scalars().all())

    async def update_availability(self, item_id: str, available: bool) -> Optional[MenuModel]:
        return await self.update(item_id, {"available": available})
