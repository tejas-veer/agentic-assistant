import asyncio
import csv
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from typing import Dict

from app.infrastructure.database.connection import async_session_factory, init_db
from app.infrastructure.database.models import (
    BusinessModel, ResourceModel, CategoryModel, MenuModel,
    UserModel, TeamMemberModel, FAQModel
)
from app.domain.shared.enums import (
    BusinessType, PaymentFlow, ResourceType, ResourceStatus,
    UserRole, TeamMemberStatus
)


SEED_DATA_PATH = Path(__file__).parent.parent.parent / "NewMigrationDocs" / "db_samples_seed"


def parse_bool(value: str) -> bool:
    return value.strip().lower() in ('true', '1', 'yes')


def parse_enum(enum_class, value: str):
    return enum_class(value.strip().lower())


def parse_datetime(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")


def read_csv(filename: str):
    filepath = SEED_DATA_PATH / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        return list(reader)


async def seed_businesses(session) -> Dict[str, int]:
    business_id_map = {}
    rows = read_csv("1_Businesses.csv")
    
    for row in rows:
        business = BusinessModel(
            name=row['name'].strip(),
            type=parse_enum(BusinessType, row['type']),
            intents=row.get('intents', '').strip() or None,
            requires_approval=parse_bool(row['requires_approval']),
            payment_flow=parse_enum(PaymentFlow, row['payment_flow']),
            payment_modes=row.get('payment_modes', '').strip().replace('"', '') or None,
            resource_type=parse_enum(ResourceType, row['resource_type']) if row.get('resource_type') else None,
            contact_phone=row.get('contact_phone', '').strip() or None,
            timings=row.get('timings', '').strip() or None,
            is_active=True
        )
        session.add(business)
        await session.flush()
        business_id_map[row['business_id'].strip()] = business.id
    
    print(f"✅ Seeded {len(rows)} businesses")
    return business_id_map


async def seed_resources(session, business_id_map: Dict[str, int]) -> Dict[str, int]:
    resource_id_map = {}
    rows = read_csv("2_Resources.csv")
    
    for row in rows:
        biz_key = row['business_id'].strip()
        if biz_key not in business_id_map:
            continue
            
        resource = ResourceModel(
            business_id=business_id_map[biz_key],
            type=parse_enum(ResourceType, row['type']),
            name=row['name'].strip(),
            capacity=int(row.get('capacity', 1)),
            status=parse_enum(ResourceStatus, row.get('status', 'available')),
            is_active=True
        )
        session.add(resource)
        await session.flush()
        resource_id_map[row['resource_id'].strip()] = resource.id
    
    print(f"✅ Seeded {len(rows)} resources")
    return resource_id_map


async def seed_categories_and_menu(session, business_id_map: Dict[str, int]) -> Dict[str, int]:
    rows = read_csv("3_Menu.csv")
    
    category_map: Dict[str, Dict[str, int]] = {}
    menu_id_map = {}
    
    for row in rows:
        biz_key = row['business_id'].strip()
        if biz_key not in business_id_map:
            continue
        
        business_id = business_id_map[biz_key]
        category_name = row['category'].strip()
        
        cat_key = f"{business_id}_{category_name}"
        if cat_key not in category_map:
            category = CategoryModel(
                business_id=business_id,
                name=category_name,
                display_order=len([k for k in category_map.keys() if k.startswith(f"{business_id}_")]),
                is_active=True
            )
            session.add(category)
            await session.flush()
            category_map[cat_key] = category.id
        
        category_id = category_map[cat_key]
        
        menu_item = MenuModel(
            business_id=business_id,
            category_id=category_id,
            name=row['name'].strip(),
            description=row.get('description', '').strip() or None,
            price=Decimal(row['price'].strip()),
            available=parse_bool(row['available']),
            quantity=int(row.get('quantity', 100)),
            preparation_time_mins=10,
            display_order=0,
            is_active=True
        )
        session.add(menu_item)
        await session.flush()
        menu_id_map[row['item_id'].strip()] = menu_item.id
    
    print(f"✅ Seeded {len(category_map)} categories")
    print(f"✅ Seeded {len(rows)} menu items")
    return menu_id_map


async def seed_users(session) -> Dict[str, int]:
    user_id_map = {}
    rows = read_csv("7_Users.csv")
    
    for row in rows:
        user = UserModel(
            name=row['name'].strip(),
            phone=row.get('phone', '').strip() or None,
            email=row.get('email', '').strip() or None,
            is_active=True
        )
        session.add(user)
        await session.flush()
        user_id_map[row['user_id'].strip()] = user.id
    
    print(f"✅ Seeded {len(rows)} users")
    return user_id_map


async def seed_team_members(session, business_id_map: Dict[str, int], user_id_map: Dict[str, int]):
    rows = read_csv("10_TeamMembers.csv")
    count = 0
    
    for row in rows:
        biz_key = row['business_id'].strip()
        user_key = row['user_id'].strip()
        
        if biz_key not in business_id_map or user_key not in user_id_map:
            continue
        
        team_member = TeamMemberModel(
            business_id=business_id_map[biz_key],
            user_id=user_id_map[user_key],
            role=parse_enum(UserRole, row.get('role', 'staff')),
            status=TeamMemberStatus.ACTIVE,
            is_active=True
        )
        session.add(team_member)
        count += 1
    
    await session.flush()
    print(f"✅ Seeded {count} team members")


async def seed_faqs(session, business_id_map: Dict[str, int]):
    rows = read_csv("6_FAQ.csv")
    count = 0
    
    for row in rows:
        biz_key = row['business_id'].strip()
        if biz_key not in business_id_map:
            continue
        
        faq = FAQModel(
            business_id=business_id_map[biz_key],
            question=row['question'].strip(),
            answer=row['answer'].strip(),
            is_active=True
        )
        session.add(faq)
        count += 1
    
    await session.flush()
    print(f"✅ Seeded {count} FAQs")


async def drop_all_tables():
    from sqlalchemy import text
    from app.infrastructure.database.connection import engine
    
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
    print("🗑️ Dropped all existing tables")


async def seed_database():
    print("🚀 Starting database seeding...")
    print(f"📁 Reading from: {SEED_DATA_PATH}")
    
    await drop_all_tables()
    await init_db()
    
    async with async_session_factory() as session:
        try:
            business_id_map = await seed_businesses(session)
            resource_id_map = await seed_resources(session, business_id_map)
            menu_id_map = await seed_categories_and_menu(session, business_id_map)
            user_id_map = await seed_users(session)
            await seed_team_members(session, business_id_map, user_id_map)
            await seed_faqs(session, business_id_map)
            
            await session.commit()
            print("\n🎉 Database seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
