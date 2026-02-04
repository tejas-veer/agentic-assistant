"""
Seed Data Script for Merged Schema
Run this to populate the database from CSV files

Usage:
    python 10_SEED_DATA_SCRIPT.py

Standard integer PKs - IDs will be auto-generated
CSV files in db_samples_seed/ are for reference data
"""

import csv
import asyncio
from pathlib import Path
from datetime import datetime
from decimal import Decimal

CSV_PATH = Path(__file__).parent / "db_samples_seed"


def parse_datetime(dt_str: str) -> datetime:
    if not dt_str or dt_str.strip() == "":
        return datetime.utcnow()
    return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")


def parse_bool(val: str) -> bool:
    return val.strip().lower() in ("true", "1", "yes")


def clean_value(val: str) -> str:
    return val.strip() if val else ""


def parse_decimal(val: str) -> Decimal:
    try:
        return Decimal(val.strip()) if val and val.strip() else Decimal("0")
    except:
        return Decimal("0")


def parse_int(val: str, default: int = 0) -> int:
    try:
        return int(val.strip()) if val and val.strip() else default
    except:
        return default


id_map = {
    "businesses": {},
    "resources": {},
    "categories": {},
    "menu": {},
    "users": {},
    "team_members": {},
    "carts": {},
    "cart_items": {},
    "bills": {},
    "addresses": {},
}

auto_id_counters = {
    "businesses": 0,
    "resources": 0,
    "categories": 0,
    "menu": 0,
    "users": 0,
    "team_members": 0,
    "carts": 0,
    "cart_items": 0,
    "bills": 0,
    "bill_items": 0,
    "addresses": 0,
    "faqs": 0,
}


def get_next_id(table: str) -> int:
    auto_id_counters[table] += 1
    return auto_id_counters[table]


async def seed_businesses(session):
    print("\n📦 Seeding Businesses...")
    with open(CSV_PATH / "1_Businesses.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("business_id", ""))
            new_id = get_next_id("businesses")
            id_map["businesses"][csv_id] = new_id

            business = {
                "id": new_id,
                "name": clean_value(row.get("name", "")),
                "type": clean_value(row.get("type", "")).lower(),
                "intents": clean_value(row.get("intents", "")),
                "requires_approval": parse_bool(row.get("requires_approval", "true")),
                "payment_flow": clean_value(row.get("payment_flow", "")).lower(),
                "payment_modes": clean_value(row.get("payment_modes", "")),
                "resource_type": clean_value(row.get("resource_type", "")).lower(),
                "contact_phone": clean_value(row.get("contact_phone", "")),
                "timings": clean_value(row.get("timings", "")),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {business['name']}")


async def seed_resources(session):
    print("\n🪑 Seeding Resources...")
    with open(CSV_PATH / "2_Resources.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("resource_id", ""))
            business_csv_id = clean_value(row.get("business_id", ""))
            new_id = get_next_id("resources")
            id_map["resources"][csv_id] = new_id

            resource = {
                "id": new_id,
                "business_id": id_map["businesses"].get(business_csv_id),
                "type": clean_value(row.get("type", "")).lower(),
                "name": clean_value(row.get("name", "")),
                "capacity": parse_int(row.get("capacity", "1"), 1),
                "meta_json": row.get("meta_json", "{}"),
                "status": clean_value(row.get("status", "available")).lower(),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {resource['name']}")


async def seed_categories(session):
    print("\n📂 Seeding Categories...")
    categories_seen = {}

    with open(CSV_PATH / "3_Menu.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            business_csv_id = clean_value(row.get("business_id", ""))
            category_name = clean_value(row.get("category", ""))
            key = f"{business_csv_id}_{category_name}"

            if key not in categories_seen:
                new_id = get_next_id("categories")
                id_map["categories"][key] = new_id
                categories_seen[key] = True

                category = {
                    "id": new_id,
                    "business_id": id_map["businesses"].get(business_csv_id),
                    "name": category_name,
                    "description": None,
                    "image_url": None,
                    "display_order": len(categories_seen),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }
                print(f"  ✓ ID {new_id}: {category_name} (Business {id_map['businesses'].get(business_csv_id)})")


async def seed_menu(session):
    print("\n🍔 Seeding Menu...")
    with open(CSV_PATH / "3_Menu.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("item_id", ""))
            business_csv_id = clean_value(row.get("business_id", ""))
            category_name = clean_value(row.get("category", ""))
            category_key = f"{business_csv_id}_{category_name}"
            new_id = get_next_id("menu")
            id_map["menu"][csv_id] = new_id

            item = {
                "id": new_id,
                "business_id": id_map["businesses"].get(business_csv_id),
                "category_id": id_map["categories"].get(category_key),
                "name": clean_value(row.get("name", "")),
                "description": clean_value(row.get("description", "")),
                "price": parse_decimal(row.get("price", "0")),
                "image_url": None,
                "available": parse_bool(row.get("available", "true")),
                "quantity": parse_int(row.get("quantity", "100"), 100),
                "preparation_time_mins": 10,
                "display_order": 0,
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {item['name']} (₹{item['price']})")


async def seed_users(session):
    print("\n👤 Seeding Users...")
    with open(CSV_PATH / "7_Users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("user_id", ""))
            new_id = get_next_id("users")
            id_map["users"][csv_id] = new_id

            user = {
                "id": new_id,
                "name": clean_value(row.get("name", "")),
                "phone": clean_value(row.get("phone", "")),
                "email": clean_value(row.get("email", "")),
                "hashed_password": None,
                "auth_provider": clean_value(row.get("auth_provider", "")),
                "auth_id": clean_value(row.get("auth_id", "")),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {user['name']}")


async def seed_team_members(session):
    print("\n👥 Seeding TeamMembers...")
    with open(CSV_PATH / "10_TeamMembers.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("member_id", ""))
            business_csv_id = clean_value(row.get("business_id", ""))
            user_csv_id = clean_value(row.get("user_id", ""))
            new_id = get_next_id("team_members")
            id_map["team_members"][csv_id] = new_id

            member = {
                "id": new_id,
                "business_id": id_map["businesses"].get(business_csv_id),
                "user_id": id_map["users"].get(user_csv_id),
                "role": clean_value(row.get("role", "staff")).lower(),
                "status": clean_value(row.get("status", "active")).lower(),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {member['role']}")


async def seed_addresses(session):
    print("\n📍 Seeding Addresses...")
    with open(CSV_PATH / "9_Addresses.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("address_id", ""))
            user_csv_id = clean_value(row.get("user_id", ""))
            new_id = get_next_id("addresses")
            id_map["addresses"][csv_id] = new_id

            address = {
                "id": new_id,
                "user_id": id_map["users"].get(user_csv_id),
                "type": clean_value(row.get("type", "home")).lower(),
                "address_line1": clean_value(row.get("address_line1", "")),
                "city": clean_value(row.get("city", "")),
                "pincode": clean_value(row.get("pincode", "")),
                "lat_long": clean_value(row.get("lat_long", "")),
                "is_active": True,
                "created_at": datetime.utcnow(),
            }
            print(f"  ✓ ID {new_id}: {address['city']}")


async def seed_carts(session):
    print("\n🛒 Seeding Carts...")
    with open(CSV_PATH / "4_Cart.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("cart_id", ""))
            user_csv_id = clean_value(row.get("user_id", ""))
            business_csv_id = clean_value(row.get("business_id", ""))
            resource_csv_id = clean_value(row.get("resource_id", ""))
            new_id = get_next_id("carts")
            id_map["carts"][csv_id] = new_id

            cart = {
                "id": new_id,
                "session_id": None,
                "device_id": None,
                "user_id": id_map["users"].get(user_csv_id) if user_csv_id else None,
                "business_id": id_map["businesses"].get(business_csv_id),
                "intent": clean_value(row.get("intent", "food_order")).lower(),
                "resource_id": id_map["resources"].get(resource_csv_id) if resource_csv_id else None,
                "customer_name": clean_value(row.get("customer_name", "")),
                "customer_phone": clean_value(row.get("customer_phone", "")),
                "item_count": parse_int(row.get("item_count", "0")),
                "subtotal": parse_decimal(row.get("subtotal", "0")),
                "tax": Decimal("0"),
                "total": Decimal("0"),
                "status": clean_value(row.get("status", "draft")).lower(),
                "source": clean_value(row.get("source", "app")).lower(),
                "notes": None,
                "estimated_ready_time": None,
                "assistant_session_id": None,
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {cart['status']}")


async def seed_cart_items(session):
    print("\n🍟 Seeding CartItems...")
    with open(CSV_PATH / "12_CartItems.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("cart_item_id", ""))
            cart_csv_id = clean_value(row.get("cart_id", ""))
            item_csv_id = clean_value(row.get("item_id", ""))
            prepared_by_csv_id = clean_value(row.get("prepared_by", ""))
            new_id = get_next_id("cart_items")
            id_map["cart_items"][csv_id] = new_id

            item = {
                "id": new_id,
                "cart_id": id_map["carts"].get(cart_csv_id),
                "item_id": id_map["menu"].get(item_csv_id),
                "item_name": clean_value(row.get("item_name", "")),
                "quantity": parse_int(row.get("quantity", "1"), 1),
                "unit_price": parse_decimal(row.get("unit_price", "0")),
                "total_price": parse_decimal(row.get("total_price", "0")),
                "notes": clean_value(row.get("notes", "")),
                "status": clean_value(row.get("status", "draft")).lower(),
                "prepared_by": id_map["team_members"].get(prepared_by_csv_id) if prepared_by_csv_id else None,
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {item['item_name']} x{item['quantity']}")


async def seed_bills(session):
    print("\n💵 Seeding Bills...")
    with open(CSV_PATH / "5_Bills.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_id = clean_value(row.get("bill_id", ""))
            cart_csv_id = clean_value(row.get("cart_id", ""))
            business_csv_id = clean_value(row.get("business_id", ""))
            new_id = get_next_id("bills")
            id_map["bills"][csv_id] = new_id

            bill = {
                "id": new_id,
                "cart_id": id_map["carts"].get(cart_csv_id),
                "business_id": id_map["businesses"].get(business_csv_id),
                "subtotal": parse_decimal(row.get("subtotal", "0")),
                "tax_percent": parse_decimal(row.get("tax_percent", "0")),
                "tax_amount": parse_decimal(row.get("tax_amount", "0")),
                "discount_amount": parse_decimal(row.get("discount_amount", "0")),
                "service_charge": parse_decimal(row.get("service_charge", "0")),
                "total_amount": parse_decimal(row.get("total_amount", "0")),
                "paid_amount": parse_decimal(row.get("paid_amount", "0")),
                "payment_mode": clean_value(row.get("payment_mode", "")).lower() or None,
                "status": clean_value(row.get("status", "pending")).lower(),
                "payment_ref": clean_value(row.get("payment_ref", "")),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: ₹{bill['total_amount']} ({bill['status']})")


async def seed_bill_items(session):
    print("\n📝 Seeding BillItems...")
    with open(CSV_PATH / "13_BillItems.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bill_csv_id = clean_value(row.get("bill_id", ""))
            cart_item_csv_id = clean_value(row.get("cart_item_id", ""))
            paid_by_csv_id = clean_value(row.get("paid_by_user_id", ""))
            new_id = get_next_id("bill_items")

            item = {
                "id": new_id,
                "bill_id": id_map["bills"].get(bill_csv_id),
                "cart_item_id": id_map["cart_items"].get(cart_item_csv_id),
                "item_name": clean_value(row.get("item_name", "")),
                "quantity": parse_int(row.get("quantity", "1"), 1),
                "unit_price": parse_decimal(row.get("unit_price", "0")),
                "total_price": parse_decimal(row.get("total_price", "0")),
                "paid_by_user_id": id_map["users"].get(paid_by_csv_id) if paid_by_csv_id else None,
                "status": clean_value(row.get("status", "unpaid")).lower(),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {item['item_name']} ({item['status']})")


async def seed_faqs(session):
    print("\n❓ Seeding FAQs...")
    with open(CSV_PATH / "6_FAQ.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            business_csv_id = clean_value(row.get("business_id", ""))
            new_id = get_next_id("faqs")

            faq = {
                "id": new_id,
                "business_id": id_map["businesses"].get(business_csv_id),
                "question": clean_value(row.get("question", "")),
                "answer": clean_value(row.get("answer", "")),
                "is_active": True,
                "created_at": parse_datetime(row.get("created_at", "")),
            }
            print(f"  ✓ ID {new_id}: {faq['question'][:40]}...")


async def main():
    print("=" * 60)
    print("🚀 SEEDING DATABASE FROM CSV FILES")
    print("=" * 60)
    print(f"📁 CSV Path: {CSV_PATH}")
    print("📝 Using auto-increment integer IDs")

    session = None

    await seed_businesses(session)
    await seed_resources(session)
    await seed_users(session)
    await seed_team_members(session)
    await seed_addresses(session)
    await seed_categories(session)
    await seed_menu(session)
    await seed_carts(session)
    await seed_cart_items(session)
    await seed_bills(session)
    await seed_bill_items(session)
    await seed_faqs(session)

    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE!")
    print("=" * 60)
    print("\n📊 Records Created:")
    for table, count in auto_id_counters.items():
        if count > 0:
            print(f"  {table}: {count}")


if __name__ == "__main__":
    asyncio.run(main())
