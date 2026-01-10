from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.repositories.menu_repository import CategoryRepository, MenuItemRepository
from app.infrastructure.database.models import CategoryModel, MenuItemModel
from app.utils.null_check import Util
from decimal import Decimal


class MenuService:
    def __init__(self, session: AsyncSession):
        self.category_repo = CategoryRepository(session)
        self.menu_item_repo = MenuItemRepository(session)
    
    async def get_full_menu(self) -> List[Dict[str, Any]]:
        categories = await self.category_repo.get_all_with_items()
        
        menu = []
        for category in categories:
            items = [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "price": float(item.price),
                    "image_url": item.image_url,
                    "is_available": item.is_available,
                    "preparation_time_mins": item.preparation_time_mins,
                    "tags": item.tags or [],
                    "customizations": item.customizations or []
                }
                for item in category.menu_items
                if item.is_active and item.is_available
            ]
            
            menu.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "image_url": category.image_url,
                "items": items
            })
        
        return menu
    
    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        item = await self.menu_item_repo.get_by_id(item_id)
        if Util.is_null(item):
            return None
        
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "image_url": item.image_url,
            "is_available": item.is_available,
            "preparation_time_mins": item.preparation_time_mins,
            "tags": item.tags or [],
            "customizations": item.customizations or []
        }
    
    async def search_menu_items(self, query: str) -> List[Dict[str, Any]]:
        items = await self.menu_item_repo.search_items(query)
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "is_available": item.is_available
            }
            for item in items
        ]
    
    async def create_category(self, name: str, description: str = None, image_url: str = None) -> CategoryModel:
        category = CategoryModel(
            name=name,
            description=description,
            image_url=image_url
        )
        return await self.category_repo.create(category)
    
    async def create_menu_item(
        self,
        name: str,
        price: Decimal,
        category_id: str,
        description: str = None,
        image_url: str = None,
        preparation_time_mins: int = 10,
        tags: List[str] = None,
        customizations: List[Dict] = None
    ) -> MenuItemModel:
        item = MenuItemModel(
            name=name,
            price=price,
            category_id=category_id,
            description=description,
            image_url=image_url,
            preparation_time_mins=preparation_time_mins,
            tags=tags or [],
            customizations=customizations or []
        )
        return await self.menu_item_repo.create(item)
    
    async def update_item_availability(self, item_id: str, is_available: bool) -> Optional[MenuItemModel]:
        return await self.menu_item_repo.update_availability(item_id, is_available)
    
    async def get_menu_for_assistant(self) -> str:
        menu = await self.get_full_menu()
        
        menu_text = "Available Menu:\n\n"
        for category in menu:
            menu_text += f"== {category['name']} ==\n"
            for item in category['items']:
                menu_text += f"- {item['name']}: ${item['price']:.2f}"
                if Util.is_not_empty(item.get('description')):
                    menu_text += f" - {item['description']}"
                menu_text += "\n"
            menu_text += "\n"
        
        return menu_text

