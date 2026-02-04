# Schema Documentation

This folder contains complete documentation for the database schema and migration guide.

## 📁 Files Overview

| File | Description |
|------|-------------|
| `01_SCHEMA_OVERVIEW.md` | Tables summary, ID conventions, user types |
| `02_ER_DIAGRAM.md` | Mermaid ER diagram with relationships |
| `03_STATUS_FLOWS.md` | Status state diagrams for Cart, CartItem, Bill |
| `04_ORDER_FLOW.md` | Complete order lifecycle with examples |
| `05_TABLE_DEFINITIONS.md` | Detailed column definitions for all tables |
| `06_MIGRATION_GUIDE.md` | Step-by-step migration from old prototype |
| `07_PYTHON_ENUMS.py` | Python enum definitions (copy to backend) |
| `08_PYTHON_MODELS.py` | SQLAlchemy models (copy to backend) |
| `09_TYPESCRIPT_TYPES.ts` | TypeScript types (copy to frontend) |
| `10_SEED_DATA_SCRIPT.py` | Script to load CSV data into database |

---

## 🚀 Quick Start

### 1. Review the Schema
Start with `01_SCHEMA_OVERVIEW.md` to understand the tables and relationships.

### 2. Understand the Flow
Read `04_ORDER_FLOW.md` to understand how orders work end-to-end.

### 3. Copy Code Files
```bash
# Copy Python enums
cp 07_PYTHON_ENUMS.py /path/to/backend/app/domain/shared/enums.py

# Copy Python models  
cp 08_PYTHON_MODELS.py /path/to/backend/app/infrastructure/database/models.py

# Copy TypeScript types
cp 09_TYPESCRIPT_TYPES.ts /path/to/frontend/src/lib/types.ts
```

### 4. Run Migrations
Follow `06_MIGRATION_GUIDE.md` for SQL migrations.

### 5. Seed Data
```bash
python 10_SEED_DATA_SCRIPT.py
```

---

## 📊 Schema Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        TABLES (11)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CORE                    USERS                   ORDERS         │
│  ════                    ═════                   ══════         │
│  1. Businesses           7. Users                4. Cart        │
│  2. Resources            9. Addresses            12. CartItems  │
│  3. Menu                 10. TeamMembers         5. Bills       │
│  6. FAQ                                          13. BillItems  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

```
User → Cart (DRAFT) → CartItems (DRAFT)
              │
              ▼
       Cart (CONFIRMED) → CartItems (PENDING)
              │
              ▼
       Cart (IN_PROGRESS) → CartItems (PREPARING → READY)
              │
              ▼
       Cart (READY) → CartItems (SERVED)
              │
              ▼
       Bill (PENDING) → BillItems (UNPAID)
              │
              ▼
       Bill (PAID) → BillItems (PAID)
              │
              ▼
       Cart (COMPLETED)
```

---

## 📝 CSV Data Files (Parent Folder)

| File | Table | Records |
|------|-------|---------|
| `1_Businesses.csv` | Businesses | 4 |
| `2_Resources.csv` | Resources | 27 |
| `3_Menu.csv` | Menu | 57 |
| `4_Cart.csv` | Cart | 8 |
| `5_Bills.csv` | Bills | 4 |
| `6_FAQ.csv` | FAQ | 30 |
| `7_Users.csv` | Users | 12 |
| `9_Addresses.csv` | Addresses | 3 |
| `10_TeamMembers.csv` | TeamMembers | 7 |
| `12_CartItems.csv` | CartItems | 16 |
| `13_BillItems.csv` | BillItems | 5 |

---

## 🎯 Integration Target

Target Prototype: `C:\Projects\DreamAi\TejasVersion\agentic-assistant`

Key differences from current prototype:
- Multi-tenant support (Businesses table)
- Resources for tables/rooms/slots
- CartItems as separate table (no JSON)
- Detailed billing with BillItems
- Split billing support
- Team member tracking
