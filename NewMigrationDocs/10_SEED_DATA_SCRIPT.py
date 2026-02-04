"""
Seed Data Script
Run this to populate the database from CSV files

Usage:
    python seed_data_script.py

Make sure to:
1. Set up your database connection in config
2. Create tables first (run migrations)
3. Update file paths if needed
"""

import csv
import asyncio
from pathlib import Path
from datetime import datetime

# Update these imports based on your project structure
# from app.infrastructure.database.connection import get_session, AsyncSession
# from app.infrastructure.database.models import (
#     BusinessModel, ResourceModel, MenuModel, UserModel,
#     TeamMemberModel, CartModel, CartItemModel, BillModel,
#     BillItemModel, AddressModel, FAQModel
# )

SHEETS_PATH = Path("sheets")


def parse_datetime(dt_str: str) -> datetime:
    if not dt_str or dt_str.strip() == "":
        return datetime.utcnow()
    return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")


def parse_bool(val: str) -> bool:
    return val.strip().lower() in ("true", "1", "yes")


def clean_value(val: str) -> str:
    return val.strip() if val else ""


async def seed_businesses(session):
    print("Seeding Businesses...")
    with open(SHEETS_PATH / "1_Businesses.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            business = {
                "business_id": clean_value(row.get("business_id", "")),
                "name": clean_value(row.get("name", "")),
                "type": clean_value(row.get("type", "")).lower(),
                "intents": clean_value(row.get("intents", "")),
                "requires_approval": parse_bool(row.get("requires_approval", "true")),
                "payment_flow": clean_value(row.get("payment_flow", "")).lower(),
                "payment_modes": clean_value(row.get("payment_modes", "")),
                "resource_type": clean_value(row.get("resource_type", "")).lower(),
                "contact_phone": clean_value(row.get("contact_phone", "")),
                "timings": clean_value(row.get("timings", "")),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {business['business_id']}: {business['name']}")
            # await session.execute(insert(BusinessModel).values(**business))
    # await session.commit()


async def seed_resources(session):
    print("Seeding Resources...")
    with open(SHEETS_PATH / "2_Resources.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            resource = {
                "resource_id": clean_value(row.get("resource_id", "")),
                "business_id": clean_value(row.get("business_id", "")),
                "type": clean_value(row.get("type", "")).lower(),
                "name": clean_value(row.get("name", "")),
                "capacity": int(row.get("capacity", 1)),
                "meta_json": row.get("meta_json", "{}"),
                "status": clean_value(row.get("status", "available")).lower(),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {resource['resource_id']}: {resource['name']}")


async def seed_menu(session):
    print("Seeding Menu...")
    with open(SHEETS_PATH / "3_Menu.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {
                "item_id": clean_value(row.get("item_id", "")),
                "business_id": clean_value(row.get("business_id", "")),
                "name": clean_value(row.get("name", "")),
                "category": clean_value(row.get("category", "")),
                "price": float(row.get("price", 0)),
                "available": parse_bool(row.get("available", "true")),
                "quantity": int(row.get("quantity", 100)),
                "description": clean_value(row.get("description", "")),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {item['item_id']}: {item['name']} (₹{item['price']})")


async def seed_users(session):
    print("Seeding Users...")
    with open(SHEETS_PATH / "7_Users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = {
                "user_id": clean_value(row.get("user_id", "")),
                "name": clean_value(row.get("name", "")),
                "phone": clean_value(row.get("phone", "")),
                "email": clean_value(row.get("email", "")),
                "auth_provider": clean_value(row.get("auth_provider", "")),
                "auth_id": clean_value(row.get("auth_id", "")),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {user['user_id']}: {user['name']}")


async def seed_team_members(session):
    print("Seeding TeamMembers...")
    with open(SHEETS_PATH / "10_TeamMembers.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            member = {
                "member_id": clean_value(row.get("member_id", "")),
                "business_id": clean_value(row.get("business_id", "")),
                "user_id": clean_value(row.get("user_id", "")),
                "role": clean_value(row.get("role", "staff")).lower(),
                "status": clean_value(row.get("status", "active")).lower(),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {member['member_id']}: {member['role']}")


async def seed_carts(session):
    print("Seeding Carts...")
    with open(SHEETS_PATH / "4_Cart.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cart = {
                "cart_id": clean_value(row.get("cart_id", "")),
                "user_id": clean_value(row.get("user_id", "")) or None,
                "business_id": clean_value(row.get("business_id", "")),
                "intent": clean_value(row.get("intent", "food_order")).lower(),
                "resource_id": clean_value(row.get("resource_id", "")) or None,
                "customer_name": clean_value(row.get("customer_name", "")),
                "customer_phone": clean_value(row.get("customer_phone", "")),
                "item_count": int(row.get("item_count", 0)),
                "subtotal": float(row.get("subtotal", 0)),
                "status": clean_value(row.get("status", "draft")).lower(),
                "source": clean_value(row.get("source", "app")).lower(),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {cart['cart_id']}: {cart['status']}")


async def seed_cart_items(session):
    print("Seeding CartItems...")
    with open(SHEETS_PATH / "12_CartItems.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {
                "cart_item_id": clean_value(row.get("cart_item_id", "")),
                "cart_id": clean_value(row.get("cart_id", "")),
                "item_id": clean_value(row.get("item_id", "")),
                "item_name": clean_value(row.get("item_name", "")),
                "quantity": int(row.get("quantity", 1)),
                "unit_price": float(row.get("unit_price", 0)),
                "total_price": float(row.get("total_price", 0)),
                "notes": clean_value(row.get("notes", "")),
                "status": clean_value(row.get("status", "draft")).lower(),
                "prepared_by": clean_value(row.get("prepared_by", "")) or None,
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {item['cart_item_id']}: {item['item_name']} x{item['quantity']}")


async def seed_bills(session):
    print("Seeding Bills...")
    with open(SHEETS_PATH / "5_Bills.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bill = {
                "bill_id": clean_value(row.get("bill_id", "")),
                "cart_id": clean_value(row.get("cart_id", "")),
                "business_id": clean_value(row.get("business_id", "")),
                "subtotal": float(row.get("subtotal", 0)),
                "tax_percent": float(row.get("tax_percent", 0)),
                "tax_amount": float(row.get("tax_amount", 0)),
                "discount_amount": float(row.get("discount_amount", 0)),
                "service_charge": float(row.get("service_charge", 0)),
                "total_amount": float(row.get("total_amount", 0)),
                "paid_amount": float(row.get("paid_amount", 0)),
                "payment_mode": clean_value(row.get("payment_mode", "")).lower() or None,
                "status": clean_value(row.get("status", "pending")).lower(),
                "payment_ref": clean_value(row.get("payment_ref", "")),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {bill['bill_id']}: ₹{bill['total_amount']} ({bill['status']})")


async def seed_bill_items(session):
    print("Seeding BillItems...")
    with open(SHEETS_PATH / "13_BillItems.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = {
                "bill_item_id": clean_value(row.get("bill_item_id", "")),
                "bill_id": clean_value(row.get("bill_id", "")),
                "cart_item_id": clean_value(row.get("cart_item_id", "")),
                "item_name": clean_value(row.get("item_name", "")),
                "quantity": int(row.get("quantity", 1)),
                "unit_price": float(row.get("unit_price", 0)),
                "total_price": float(row.get("total_price", 0)),
                "paid_by_user_id": clean_value(row.get("paid_by_user_id", "")) or None,
                "status": clean_value(row.get("status", "unpaid")).lower(),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {item['bill_item_id']}: {item['item_name']} ({item['status']})")


async def seed_addresses(session):
    print("Seeding Addresses...")
    with open(SHEETS_PATH / "9_Addresses.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            address = {
                "address_id": clean_value(row.get("address_id", "")),
                "user_id": clean_value(row.get("user_id", "")),
                "type": clean_value(row.get("type", "home")).lower(),
                "address_line1": clean_value(row.get("address_line1", "")),
                "city": clean_value(row.get("city", "")),
                "pincode": clean_value(row.get("pincode", "")),
                "lat_long": clean_value(row.get("lat_long", "")),
            }
            print(f"  - {address['address_id']}: {address['city']}")


async def seed_faqs(session):
    print("Seeding FAQs...")
    with open(SHEETS_PATH / "6_FAQ.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            faq = {
                "business_id": clean_value(row.get("business_id", "")),
                "question": clean_value(row.get("question", "")),
                "answer": clean_value(row.get("answer", "")),
                "created_at": parse_datetime(row.get("created_at", "")),
                "updated_at": parse_datetime(row.get("updated_at", "")),
            }
            print(f"  - {faq['business_id']}: {faq['question'][:50]}...")


async def main():
    print("=" * 60)
    print("SEEDING DATABASE FROM CSV FILES")
    print("=" * 60)
    
    # Get database session
    # async with get_session() as session:
    session = None  # Replace with actual session
    
    await seed_businesses(session)
    await seed_resources(session)
    await seed_menu(session)
    await seed_users(session)
    await seed_team_members(session)
    await seed_addresses(session)
    await seed_carts(session)
    await seed_cart_items(session)
    await seed_bills(session)
    await seed_bill_items(session)
    await seed_faqs(session)
    
    print("=" * 60)
    print("SEEDING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
