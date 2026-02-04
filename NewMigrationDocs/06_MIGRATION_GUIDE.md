# Migration Guide: Old Prototype → New Schema

## Overview

This guide helps migrate from the existing prototype at:
`C:\Projects\DreamAi\TejasVersion\agentic-assistant`

To the new schema defined in this folder.

> **Note:** All tables use UUID (String 36) as primary keys.

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
| `categories` + `menu_items` | `Categories` + `Menu` tables | **UPDATE** |

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

Run the SQL migrations in this order (PostgreSQL syntax):

```sql
-- 1. Businesses (new)
CREATE TABLE businesses (
    id VARCHAR(36) PRIMARY KEY,
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

-- 3. Categories (per-business)
CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) REFERENCES businesses(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 4. Menu
CREATE TABLE menu (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) REFERENCES businesses(id),
    category_id VARCHAR(36) REFERENCES categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    available BOOLEAN DEFAULT TRUE,
    quantity INTEGER DEFAULT 100,
    preparation_time_mins INTEGER DEFAULT 10,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 5. Users
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    hashed_password VARCHAR(255),
    auth_provider VARCHAR(50),
    auth_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 6. TeamMembers (new)
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) REFERENCES businesses(id),
    user_id VARCHAR(36) REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'staff',
    status VARCHAR(20) DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 7. Addresses (new)
CREATE TABLE addresses (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    type VARCHAR(20),
    address_line1 VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    lat_long VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 8. AssistantSessions (existing - keep)
CREATE TABLE assistant_sessions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    assistant_type VARCHAR(20) NOT NULL,
    device_id VARCHAR(100),
    phone_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    context JSON DEFAULT '{}',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 9. Carts
CREATE TABLE carts (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(100),
    device_id VARCHAR(100),
    user_id VARCHAR(36) REFERENCES users(id),
    business_id VARCHAR(36) REFERENCES businesses(id),
    intent VARCHAR(20) DEFAULT 'food_order',
    resource_id VARCHAR(36) REFERENCES resources(id),
    customer_name VARCHAR(200),
    customer_phone VARCHAR(20),
    item_count INTEGER DEFAULT 0,
    subtotal DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    source VARCHAR(20) DEFAULT 'app',
    notes TEXT,
    estimated_ready_time INTEGER,
    assistant_session_id VARCHAR(36) REFERENCES assistant_sessions(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 10. CartItems (new)
CREATE TABLE cart_items (
    id VARCHAR(36) PRIMARY KEY,
    cart_id VARCHAR(36) REFERENCES carts(id),
    item_id VARCHAR(36) REFERENCES menu(id),
    item_name VARCHAR(200) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    prepared_by VARCHAR(36) REFERENCES team_members(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 11. Bills (new)
CREATE TABLE bills (
    id VARCHAR(36) PRIMARY KEY,
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

-- 12. BillItems (new)
CREATE TABLE bill_items (
    id VARCHAR(36) PRIMARY KEY,
    bill_id VARCHAR(36) REFERENCES bills(id),
    cart_item_id VARCHAR(36) REFERENCES cart_items(id),
    item_name VARCHAR(200) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    paid_by_user_id VARCHAR(36) REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'unpaid',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 13. FAQ (new)
CREATE TABLE faqs (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) REFERENCES businesses(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 14. ConversationMessages (existing - keep)
CREATE TABLE conversation_messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES assistant_sessions(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    audio_url VARCHAR(500),
    intent VARCHAR(100),
    entities JSON DEFAULT '{}',
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Devices (existing - keep)
CREATE TABLE devices (
    id VARCHAR(36) PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    device_type VARCHAR(20),
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Step 3: Seed Initial Data

Use the seed script:

```bash
cd backend
python -m scripts.seed_data
```

The seed script will:
1. Drop all existing tables
2. Create new tables based on SQLAlchemy models
3. Load data from CSV files in `/db_samples_seed` folder
4. Generate UUIDs for all records
5. Map CSV reference IDs to UUIDs for foreign keys

---

## Code Changes Required

### 1. Update Enums (`backend/app/domain/shared/enums.py`)

See `07_PYTHON_ENUMS.py` in this folder.

### 2. Update Models (`backend/app/infrastructure/database/models.py`)

See `08_PYTHON_MODELS.py` in this folder.

Key changes:
- All `id` columns are `String(36)` with UUID default
- All foreign keys are `String(36)`

### 3. Update Services

Key changes needed:

#### CartService
- Remove JSON item handling
- Use CartItems table instead
- Add business_id context
- All IDs are strings (UUID)

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

Key changes:
- All `id` fields are `string` (not `number`)
- All foreign key fields are `string`

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
