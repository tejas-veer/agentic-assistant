from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base_repository import BaseRepository
from ..models import CategoryModel, MenuItemModel


class CategoryRepository(BaseRepository[CategoryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CategoryModel)
    
    async def get_all_with_items(self) -> List[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .where(CategoryModel.is_active == True)
            .options(selectinload(CategoryModel.menu_items))
            .order_by(CategoryModel.display_order)
        )
        return list(result.scalars().all())


class MenuItemRepository(BaseRepository[MenuItemModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MenuItemModel)
    
    async def get_by_category(self, category_id: str) -> List[MenuItemModel]:
        result = await self.session.execute(
            select(MenuItemModel)
            .where(
                MenuItemModel.category_id == category_id,
                MenuItemModel.is_active == True,
                MenuItemModel.is_available == True
            )
        )
        return list(result.scalars().all())
    
    async def get_available_items(self) -> List[MenuItemModel]:
        result = await self.session.execute(
            select(MenuItemModel)
            .where(
                MenuItemModel.is_active == True,
                MenuItemModel.is_available == True
            )
        )
        return list(result.scalars().all())
    
    async def search_items(self, query: str) -> List[MenuItemModel]:
        result = await self.session.execute(
            select(MenuItemModel)
            .where(
                MenuItemModel.is_active == True,
                MenuItemModel.is_available == True,
                MenuItemModel.name.ilike(f"%{query}%")
            )
        )
        return list(result.scalars().all())
    
    async def update_availability(self, item_id: str, is_available: bool) -> Optional[MenuItemModel]:
        return await self.update(item_id, {"is_available": is_available})

