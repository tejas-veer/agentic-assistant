# Database Schema Overview

> **Note:** All tables use UUID (String 36 chars) as primary keys for better multi-tenancy and security.

## Tables Summary

| # | File | Table Name | Records | Purpose |
|---|------|------------|---------|---------|
| 1 | `1_Businesses.csv` | Businesses | 4 | Multi-tenant business config |
| 2 | `2_Resources.csv` | Resources | 27 | Tables, Rooms, Slots |
| 3 | `3_Menu.csv` | Menu | 57 | Items/Services catalog |
| 4 | `4_Cart.csv` | Cart | 8 | Order parent record |
| 5 | `5_Bills.csv` | Bills | 4 | Payment tracking |
| 6 | `6_FAQ.csv` | FAQ | 30 | Help content per business |
| 7 | `7_Users.csv` | Users | 12 | User accounts |
| 9 | `9_Addresses.csv` | Addresses | 3 | User delivery addresses |
| 10 | `10_TeamMembers.csv` | TeamMembers | 7 | Staff & roles |
| 12 | `12_CartItems.csv` | CartItems | 16 | Individual cart items |
| 13 | `13_BillItems.csv` | BillItems | 5 | Split billing items |

---

## Primary Key Strategy

All tables use **UUID** (36-character string) as primary keys:

```python
import uuid
def generate_uuid():
    return str(uuid.uuid4())
```

**Benefits:**
- ✅ Multi-tenant safe - no ID conflicts across businesses
- ✅ Security - IDs are not guessable
- ✅ Scalability - works in distributed systems
- ✅ No sequential pattern exposure

---

## Business Types Supported

| Business | Type | Intent | Resource | Payment Flow |
|----------|------|--------|----------|--------------|
| Spiceclub Restaurant | RESTAURANT | FOOD_ORDER | TABLE | POST_SERVICE |
| Grand Palace Hotel | HOTEL | BOOKING | ROOM | PRE_SERVICE |
| Dr. Sharma Clinic | CLINIC | APPOINTMENT | SLOT | PRE_SERVICE |
| PacDonalds | RESTAURANT | FOOD_ORDER | TABLE | POST_SERVICE |

---

## CSV ID Prefixes (Reference Only)

> **Note:** These prefixes are only in CSV files for readability. The actual database uses UUIDs.

| Table | Prefix | Example |
|-------|--------|---------|
| Businesses | BIZ | BIZ001, BIZ004 |
| Resources (Tables) | T, P | T01, P01 |
| Resources (Rooms) | R | R101, R201 |
| Resources (Slots) | S | S01, S02 |
| Menu (Spiceclub) | M | M001-M022 |
| Menu (PacDonalds) | F | F001-F021 |
| Menu (Hotel) | H | H001-H007 |
| Menu (Clinic) | D | D001-D006 |
| Users | U | U001-U012 |
| TeamMembers | TM | TM001-TM007 |
| Cart | CART | CART001-CART008 |
| CartItems | CI | CI001-CI016 |
| Bills | BILL | BILL001-BILL004 |
| BillItems | BI | BI001-BI005 |
| Addresses | ADDR | ADDR001-ADDR003 |

---

## User Types

### Team Members (Staff)

| user_id | Name | Business | Role |
|---------|------|----------|------|
| U001 | Admin Rahul | Spiceclub | ADMIN |
| U002 | Admin Priya | Spiceclub | ADMIN |
| U003 | Staff Raju | Spiceclub | STAFF |
| U004 | Staff Sita | Spiceclub | STAFF |
| U008 | Admin Rocky | PacDonalds | ADMIN |
| U009 | Staff Bunty | PacDonalds | STAFF |
| U010 | Staff Pinky | PacDonalds | STAFF |

### Customers

| user_id | Name | Description |
|---------|------|-------------|
| U005 | Customer Amit | Spiceclub regular |
| U006 | Customer Neha | Spiceclub regular |
| U007 | Guest User | Walk-in guest |
| U011 | Customer Raj | PacDonalds regular |
| U012 | Customer Simran | PacDonalds regular |

---

## Role Permissions

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full access - manage cart, approve orders, update payments, manage menu, add staff |
| **STAFF** | Read-only - view orders on kitchen display system |
