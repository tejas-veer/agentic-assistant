# Schema Documentation (Merged Schema)

> **Updated:** UUID (String 36) primary keys for all tables

## 📁 Files Overview

| File | Description |
|------|-------------|
| `01_SCHEMA_OVERVIEW.md` | Tables summary, ID conventions, user types |
| `02_ER_DIAGRAM.md` | Mermaid ER diagram with all relationships |
| `03_STATUS_FLOWS.md` | Status state diagrams for Cart, CartItem, Bill |
| `04_ORDER_FLOW.md` | Complete order lifecycle with examples |
| `05_TABLE_DEFINITIONS.md` | **Detailed column definitions (MERGED)** |
| `06_MIGRATION_GUIDE.md` | Step-by-step migration from old prototype |
| `07_PYTHON_ENUMS.py` | **Python enum definitions (MERGED)** |
| `08_PYTHON_MODELS.py` | **SQLAlchemy models (MERGED)** |
| `09_TYPESCRIPT_TYPES.ts` | **TypeScript types (MERGED)** |
| `10_SEED_DATA_SCRIPT.py` | Script to load CSV data into database |

---

## 🚀 Quick Start

### 1. Review the Schema
Start with `05_TABLE_DEFINITIONS.md` to understand all tables and columns.

### 2. Understand the Flow
Read `04_ORDER_FLOW.md` to understand how orders work end-to-end.

### 3. Copy Code Files
```bash
# Copy Python enums
cp 07_PYTHON_ENUMS.py ../backend/app/domain/shared/enums.py

# Copy Python models
cp 08_PYTHON_MODELS.py ../backend/app/infrastructure/database/models.py

# Copy TypeScript types
cp 09_TYPESCRIPT_TYPES.ts ../frontend/src/lib/types.ts
```

### 4. Run Migrations
Follow `06_MIGRATION_GUIDE.md` for SQL migrations.

### 5. Seed Data
```bash
cd NewMigrationDocs
python 10_SEED_DATA_SCRIPT.py
```

---

## 📊 Schema Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TABLES (15)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NEW TABLES              MERGED TABLES           EXISTING (KEPT)            │
│  ══════════              ═════════════           ═══════════════            │
│  1. Businesses           3. Categories           13. AssistantSessions      │
│  2. Resources            4. Menu                 14. ConversationMessages   │
│  6. TeamMembers          5. Users                15. Devices                │
│  7. Addresses            8. Cart                                            │
│  9. CartItems                                                               │
│  10. Bills                                                                  │
│  11. BillItems                                                              │
│  12. FAQ                                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Primary Key Strategy

All tables use **UUID (36-character string)** primary keys:

```python
import uuid
def generate_uuid():
    return str(uuid.uuid4())
```

**SQLAlchemy Example:**
```python
id = Column(String(36), primary_key=True, default=generate_uuid)
```

**TypeScript:**
```typescript
interface User {
  id: string  // UUID
  // ...
}
```

**Benefits of UUID:**
- ✅ Multi-tenant safe - no ID conflicts across businesses
- ✅ Security - IDs are not guessable/enumerable
- ✅ Scalability - works in distributed systems
- ✅ No sequential pattern exposure

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

## 📝 CSV Data Files (Reference Data)

| File | Table | Records |
|------|-------|---------|
| `db_samples_seed/1_Businesses.csv` | Businesses | 4 |
| `db_samples_seed/2_Resources.csv` | Resources | 27 |
| `db_samples_seed/3_Menu.csv` | Menu + Categories | 57 |
| `db_samples_seed/4_Cart.csv` | Cart | 8 |
| `db_samples_seed/5_Bills.csv` | Bills | 4 |
| `db_samples_seed/6_FAQ.csv` | FAQ | 30 |
| `db_samples_seed/7_Users.csv` | Users | 12 |
| `db_samples_seed/9_Addresses.csv` | Addresses | 3 |
| `db_samples_seed/10_TeamMembers.csv` | TeamMembers | 7 |
| `db_samples_seed/12_CartItems.csv` | CartItems | 16 |
| `db_samples_seed/13_BillItems.csv` | BillItems | 5 |

> Note: CSV IDs (like BIZ001, U001) are for reference only. Actual database uses generated UUIDs with mapping.

---

## 🎯 Key Changes from Original Prototype

| Feature | Old Prototype | New Schema |
|---------|--------------|------------|
| Primary Keys | UUID strings | UUID strings (String 36) |
| Multi-tenant | ❌ Single business | ✅ Businesses table |
| Categories | Global | Per-business (business_id FK) |
| Menu | Basic | + image_url, prep_time, display_order |
| Cart items | JSON in Cart | Separate CartItems table |
| Orders | Separate table | Merged into Cart with status flow |
| Billing | None | Bills + BillItems (split billing) |
| Resources | table_number string | Resources table (tables/rooms/slots) |
| Users | Basic auth | + auth_provider, auth_id |
| Assistant | ✅ Kept | + FK from Cart |
| Devices | ✅ Kept | Unchanged |

---

## 🔗 Integration Target

**Target Prototype:** `C:\Projects\DreamAi\TejasVersion\agentic-assistant`

### Backend Updates Needed:
1. `backend/app/domain/shared/enums.py` ← `07_PYTHON_ENUMS.py`
2. `backend/app/infrastructure/database/models.py` ← `08_PYTHON_MODELS.py`
3. Update services (CartService, MenuService, new BillService)
4. Update API routers

### Frontend Updates Needed:
1. `frontend/src/lib/types.ts` ← `09_TYPESCRIPT_TYPES.ts`
2. Update API calls in `frontend/src/lib/api.ts`
3. Update store in `frontend/src/lib/store.ts`
4. Update components
