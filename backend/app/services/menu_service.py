from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.repositories import CategoryRepository, MenuRepository
from app.infrastructure.database.models import CategoryModel, MenuModel
from app.utils.null_check import Util
from decimal import Decimal


class MenuService:
    def __init__(self, session: AsyncSession):
        self.category_repo = CategoryRepository(session)
        self.menu_repo = MenuRepository(session)

    async def get_full_menu(self, business_id: str) -> List[Dict[str, Any]]:
        categories = await self.category_repo.get_all_with_items(business_id)

        menu = []
        for category in categories:
            items = [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "price": float(item.price),
                    "image_url": item.image_url,
                    "available": item.available,
                    "quantity": item.quantity,
                    "preparation_time_mins": item.preparation_time_mins,
                    "display_order": item.display_order
                }
                for item in category.menu_items
                if item.is_active and item.available
            ]

            menu.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "image_url": category.image_url,
                "display_order": category.display_order,
                "items": items
            })

        return menu

    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        item = await self.menu_repo.get_by_id(item_id)
        if Util.is_null(item):
            return None

        return {
            "id": item.id,
            "business_id": item.business_id,
            "category_id": item.category_id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "image_url": item.image_url,
            "available": item.available,
            "quantity": item.quantity,
            "preparation_time_mins": item.preparation_time_mins,
            "display_order": item.display_order
        }

    async def search_menu_items(self, business_id: str, query: str) -> List[Dict[str, Any]]:
        items = await self.menu_repo.search_items(business_id, query)
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "available": item.available
            }
            for item in items
        ]

    async def create_category(
        self,
        business_id: str,
        name: str,
        description: str = None,
        image_url: str = None
    ) -> CategoryModel:
        category = CategoryModel(
            business_id=business_id,
            name=name,
            description=description,
            image_url=image_url
        )
        return await self.category_repo.create(category)

    async def create_menu_item(
        self,
        business_id: str,
        category_id: str,
        name: str,
        price: Decimal,
        description: str = None,
        image_url: str = None,
        preparation_time_mins: int = 10,
        quantity: int = 100
    ) -> MenuModel:
        item = MenuModel(
            business_id=business_id,
            category_id=category_id,
            name=name,
            price=price,
            description=description,
            image_url=image_url,
            preparation_time_mins=preparation_time_mins,
            quantity=quantity
        )
        return await self.menu_repo.create(item)

    async def update_item_availability(self, item_id: str, available: bool) -> Optional[MenuModel]:
        return await self.menu_repo.update_availability(item_id, available)

    async def get_menu_for_assistant(self, business_id: str) -> str:
        menu = await self.get_full_menu(business_id)

        menu_text = "Available Menu:\n\n"
        for category in menu:
            menu_text += f"== {category['name']} ==\n"
            for item in category['items']:
                menu_text += f"- {item['name']}: ₹{item['price']:.2f}"
                if Util.is_not_empty(item.get('description')):
                    menu_text += f" - {item['description']}"
                menu_text += "\n"
            menu_text += "\n"

        return menu_text
