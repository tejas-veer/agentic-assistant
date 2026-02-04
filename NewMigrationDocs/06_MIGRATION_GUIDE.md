# Migration Guide: Old Prototype → New Schema

## Overview

This guide helps migrate from the existing prototype at:
`C:\Projects\DreamAi\TejasVersion\agentic-assistant`

To the new schema defined in this folder.

---

## Current vs New Schema Comparison

| Current Prototype | New Schema | Action |
|-------------------|------------|--------|
| No multi-tenant | `Businesses` table | **ADD** |
| `table_number` string in Order | `Resources` table + FK | **ADD + MIGRATE** |
| `orders` table | `Cart` table | **RENAME** |
| `items` as JSON in Order/Cart | `CartItems` table | **EXTRACT TO TABLE** |
| `carts` table (session-based) | Merged into `Cart` | **MERGE** |
| No billing details | `Bills` + `BillItems` | **ADD** |
| Basic `users` table | Enhanced `Users` + `TeamMembers` | **UPDATE + ADD** |
| `categories` + `menu_items` | Single `Menu` table | **SIMPLIFY** |

---

## Step-by-Step Migration

### Step 1: Backup Current Database

```bash
# If using SQLite
cp database.db database_backup.db

# If using PostgreSQL
pg_dump -U username dbname > backup.sql
```

### Step 2: Create New Tables

Run the SQL migrations in this order:

```sql
-- 1. Businesses (new)
CREATE TABLE businesses (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL,
    intents VARCHAR(100),
    requires_approval BOOLEAN DEFAULT TRUE,
    payment_flow VARCHAR(20) DEFAULT 'post_service',
    payment_modes VARCHAR(100),
    resource_type VARCHAR(20),
    contact_phone VARCHAR(20),
    timings VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 2. Resources (new)
CREATE TABLE resources (
    id VARCHAR(36) PRIMARY KEY,
    resource_id VARCHAR(20) UNIQUE NOT NULL,
    business_id VARCHAR(36) REFERENCES businesses(id),
    type VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    capacity INTEGER DEFAULT 1,
    meta_json JSON,
    status VARCHAR(20) DEFAULT 'available',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 3. Menu (replace categories + menu_items)
CREATE TABLE menu (
    id VARCHAR(36) PRIMARY KEY,
    item_id VARCHAR(20) UNIQUE NOT NULL,
    business_id VARCHAR(36) REFERENCES businesses(id),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    quantity INTEGER DEFAULT 100,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 4. Update Users table
ALTER TABLE users ADD COLUMN user_id VARCHAR(20);
ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50);
ALTER TABLE users ADD COLUMN auth_id VARCHAR(255);
-- Remove old columns if needed

-- 5. TeamMembers (new)
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY,
    member_id VARCHAR(20) UNIQUE NOT NULL,
    business_id VARCHAR(36) REFERENCES businesses(id),
    user_id VARCHAR(36) REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'staff',
    status VARCHAR(20) DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 6. Rename/Update Carts table
ALTER TABLE carts RENAME TO carts_old;

CREATE TABLE carts (
    id VARCHAR(36) PRIMARY KEY,
    cart_id VARCHAR(20) UNIQUE NOT NULL,
    user_id VARCHAR(36) REFERENCES users(id),
    business_id VARCHAR(36) REFERENCES businesses(id),
    intent VARCHAR(20) DEFAULT 'food_order',
    resource_id VARCHAR(36) REFERENCES resources(id),
    customer_name VARCHAR(200),
    customer_phone VARCHAR(20),
    item_count INTEGER DEFAULT 0,
    subtotal DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    source VARCHAR(20) DEFAULT 'app',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 7. CartItems (new - replaces JSON items)
CREATE TABLE cart_items (
    id VARCHAR(36) PRIMARY KEY,
    cart_item_id VARCHAR(20) UNIQUE NOT NULL,
    cart_id VARCHAR(36) REFERENCES carts(id),
    item_id VARCHAR(36) REFERENCES menu(id),
    item_name VARCHAR(200),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    prepared_by VARCHAR(36) REFERENCES team_members(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 8. Bills (new)
CREATE TABLE bills (
    id VARCHAR(36) PRIMARY KEY,
    bill_id VARCHAR(20) UNIQUE NOT NULL,
    cart_id VARCHAR(36) REFERENCES carts(id),
    business_id VARCHAR(36) REFERENCES businesses(id),
    subtotal DECIMAL(10,2) DEFAULT 0,
    tax_percent DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    service_charge DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    paid_amount DECIMAL(10,2) DEFAULT 0,
    payment_mode VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    payment_ref VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 9. BillItems (new)
CREATE TABLE bill_items (
    id VARCHAR(36) PRIMARY KEY,
    bill_item_id VARCHAR(20) UNIQUE NOT NULL,
    bill_id VARCHAR(36) REFERENCES bills(id),
    cart_item_id VARCHAR(36) REFERENCES cart_items(id),
    item_name VARCHAR(200),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    paid_by_user_id VARCHAR(36) REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'unpaid',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 10. Addresses (new)
CREATE TABLE addresses (
    id VARCHAR(36) PRIMARY KEY,
    address_id VARCHAR(20) UNIQUE NOT NULL,
    user_id VARCHAR(36) REFERENCES users(id),
    type VARCHAR(20),
    address_line1 VARCHAR(500),
    city VARCHAR(100),
    pincode VARCHAR(20),
    lat_long VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 11. FAQ (new)
CREATE TABLE faqs (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) REFERENCES businesses(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Step 3: Migrate Data

```sql
-- Migrate menu items (merge category into menu)
INSERT INTO menu (id, item_id, business_id, name, category, price, available, description)
SELECT 
    mi.id,
    CONCAT('M', LPAD(ROW_NUMBER() OVER (), 3, '0')),
    'your_business_id',
    mi.name,
    c.name,
    mi.price,
    mi.is_available,
    mi.description
FROM menu_items mi
LEFT JOIN categories c ON mi.category_id = c.id;

-- Migrate carts (extract items JSON to cart_items)
-- This requires application code - see Python script below
```

### Step 4: Seed Initial Data

Load data from CSV files in `/sheets` folder:

```python
import csv
import asyncio
from app.infrastructure.database.connection import get_session

async def seed_from_csv():
    async with get_session() as session:
        # Load businesses
        with open('sheets/1_Businesses.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Insert into businesses table
                pass
        
        # Repeat for other CSV files...
```

---

## Code Changes Required

### 1. Update Enums (`backend/app/domain/shared/enums.py`)

See `07_PYTHON_ENUMS.py` in this folder.

### 2. Update Models (`backend/app/infrastructure/database/models.py`)

See `08_PYTHON_MODELS.py` in this folder.

### 3. Update Services

Key changes needed:

#### CartService
- Remove JSON item handling
- Use CartItems table instead
- Add business_id context

#### OrderService  
- Rename to CartService (or keep as alias)
- Update status enums
- Add resource assignment

#### BillService (new)
- Create bill from cart
- Handle split billing
- Process payments

---

## Frontend Changes

### Update TypeScript Types (`frontend/src/lib/types.ts`)

See `09_TYPESCRIPT_TYPES.ts` in this folder.

---

## Testing Checklist

- [ ] Create business (seed data)
- [ ] Create resources (seed data)
- [ ] Create menu items (seed data)
- [ ] User registration/login
- [ ] Add items to cart (creates CartItems)
- [ ] Confirm order (status transitions)
- [ ] Kitchen updates item status
- [ ] Generate bill
- [ ] Process payment
- [ ] Complete order
- [ ] Split billing scenario
