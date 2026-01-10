import asyncio
from decimal import Decimal
from app.infrastructure.database.connection import async_session_factory, init_db
from app.infrastructure.database.models import CategoryModel, MenuItemModel


SAMPLE_MENU = {
    "Burgers": [
        {"name": "Classic Burger", "price": Decimal("9.99"), "description": "Beef patty with lettuce, tomato, onion", "preparation_time_mins": 12},
        {"name": "Cheese Burger", "price": Decimal("10.99"), "description": "Classic burger with melted cheddar", "preparation_time_mins": 12},
        {"name": "Bacon Burger", "price": Decimal("12.99"), "description": "Cheese burger with crispy bacon", "preparation_time_mins": 15},
        {"name": "Veggie Burger", "price": Decimal("10.49"), "description": "Plant-based patty with fresh vegetables", "preparation_time_mins": 12},
    ],
    "Pizzas": [
        {"name": "Margherita", "price": Decimal("12.99"), "description": "Fresh mozzarella, tomato, basil", "preparation_time_mins": 18},
        {"name": "Pepperoni", "price": Decimal("14.99"), "description": "Classic pepperoni with mozzarella", "preparation_time_mins": 18},
        {"name": "BBQ Chicken", "price": Decimal("15.99"), "description": "Grilled chicken, BBQ sauce, red onion", "preparation_time_mins": 20},
        {"name": "Veggie Supreme", "price": Decimal("13.99"), "description": "Bell peppers, mushrooms, olives, onions", "preparation_time_mins": 18},
    ],
    "Sides": [
        {"name": "French Fries", "price": Decimal("4.49"), "description": "Crispy golden fries", "preparation_time_mins": 8},
        {"name": "Onion Rings", "price": Decimal("5.49"), "description": "Beer-battered onion rings", "preparation_time_mins": 8},
        {"name": "Mozzarella Sticks", "price": Decimal("6.99"), "description": "Breaded mozzarella with marinara", "preparation_time_mins": 10},
        {"name": "Garden Salad", "price": Decimal("5.99"), "description": "Fresh mixed greens", "preparation_time_mins": 5},
    ],
    "Drinks": [
        {"name": "Coca-Cola", "price": Decimal("2.49"), "description": "Classic cola", "preparation_time_mins": 1},
        {"name": "Sprite", "price": Decimal("2.49"), "description": "Lemon-lime soda", "preparation_time_mins": 1},
        {"name": "Iced Tea", "price": Decimal("2.99"), "description": "Fresh brewed iced tea", "preparation_time_mins": 2},
        {"name": "Lemonade", "price": Decimal("3.49"), "description": "Fresh squeezed lemonade", "preparation_time_mins": 3},
    ],
    "Desserts": [
        {"name": "Chocolate Brownie", "price": Decimal("5.99"), "description": "Warm brownie with vanilla ice cream", "preparation_time_mins": 8},
        {"name": "Cheesecake", "price": Decimal("6.99"), "description": "New York style cheesecake", "preparation_time_mins": 5},
        {"name": "Apple Pie", "price": Decimal("5.49"), "description": "Warm apple pie with cinnamon", "preparation_time_mins": 8},
    ]
}


async def seed_database():
    await init_db()
    
    async with async_session_factory() as session:
        display_order = 0
        for category_name, items in SAMPLE_MENU.items():
            category = CategoryModel(
                name=category_name,
                display_order=display_order
            )
            session.add(category)
            await session.flush()
            
            for item_data in items:
                menu_item = MenuItemModel(
                    name=item_data["name"],
                    price=item_data["price"],
                    description=item_data["description"],
                    category_id=category.id,
                    preparation_time_mins=item_data["preparation_time_mins"],
                    tags=[],
                    customizations=[]
                )
                session.add(menu_item)
            
            display_order += 1
        
        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())

