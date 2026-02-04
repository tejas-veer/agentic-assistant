# Table Definitions

## 1. Businesses

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| business_id | string(20) | NO | Primary Key (BIZ001) |
| name | string(200) | NO | Business name |
| type | enum | NO | RESTAURANT, HOTEL, CLINIC |
| intents | string(100) | YES | FOOD_ORDER, BOOKING, APPOINTMENT |
| requires_approval | boolean | NO | Whether orders need admin approval |
| payment_flow | enum | NO | PRE_SERVICE, POST_SERVICE |
| payment_modes | string(100) | YES | CASH,UPI,CARD |
| resource_type | enum | YES | TABLE, ROOM, SLOT |
| contact_phone | string(20) | YES | Business contact |
| timings | string(100) | YES | Operating hours |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 2. Resources

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| resource_id | string(20) | NO | Primary Key (T01, P01, R101, S01) |
| business_id | string(20) | NO | FK → Businesses |
| type | enum | NO | TABLE, ROOM, SLOT |
| name | string(200) | NO | Display name |
| capacity | int | NO | Max guests |
| meta_json | json | YES | {location, ac, floor, view} |
| status | enum | NO | AVAILABLE, ASSIGNED |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 3. Menu

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| item_id | string(20) | NO | Primary Key (M001, F001) |
| business_id | string(20) | NO | FK → Businesses |
| name | string(200) | NO | Item name |
| category | string(100) | YES | Category name |
| price | decimal(10,2) | NO | Item price |
| available | boolean | NO | Is item available |
| quantity | int | YES | Stock quantity |
| description | text | YES | Item description |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 4. Cart

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| cart_id | string(20) | NO | Primary Key (CART001) |
| user_id | string(20) | YES | FK → Users (nullable for guests) |
| business_id | string(20) | NO | FK → Businesses |
| intent | enum | NO | FOOD_ORDER, BOOKING, APPOINTMENT |
| resource_id | string(20) | YES | FK → Resources (nullable for DRAFT) |
| customer_name | string(200) | YES | Customer name |
| customer_phone | string(20) | YES | Customer phone |
| item_count | int | NO | Total items count |
| subtotal | decimal(10,2) | NO | Sum of CartItems.total_price |
| status | enum | NO | DRAFT, CONFIRMED, IN_PROGRESS, READY, COMPLETED, ABANDONED, CANCELLED |
| source | enum | NO | APP, VOICE, CHAT |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 5. CartItems

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| cart_item_id | string(20) | NO | Primary Key (CI001) |
| cart_id | string(20) | NO | FK → Cart |
| item_id | string(20) | NO | FK → Menu |
| item_name | string(200) | NO | Denormalized item name |
| quantity | int | NO | Quantity ordered |
| unit_price | decimal(10,2) | NO | Price per unit |
| total_price | decimal(10,2) | NO | quantity × unit_price |
| notes | text | YES | Special instructions |
| status | enum | NO | DRAFT, PENDING, PREPARING, READY, SERVED, ABANDONED, CANCELLED |
| prepared_by | string(20) | YES | FK → TeamMembers |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 6. Bills

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| bill_id | string(20) | NO | Primary Key (BILL001) |
| cart_id | string(20) | NO | FK → Cart |
| business_id | string(20) | NO | FK → Businesses |
| subtotal | decimal(10,2) | NO | Sum before tax |
| tax_percent | decimal(5,2) | NO | Tax percentage |
| tax_amount | decimal(10,2) | NO | Calculated tax |
| discount_amount | decimal(10,2) | NO | Discount applied |
| service_charge | decimal(10,2) | NO | Service charge |
| total_amount | decimal(10,2) | NO | Final amount |
| paid_amount | decimal(10,2) | NO | Amount paid |
| payment_mode | enum | YES | CASH, UPI, CARD |
| status | enum | NO | PENDING, PARTIAL, PAID, REFUNDED |
| payment_ref | string(100) | YES | Payment reference |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 7. BillItems

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| bill_item_id | string(20) | NO | Primary Key (BI001) |
| bill_id | string(20) | NO | FK → Bills |
| cart_item_id | string(20) | NO | FK → CartItems |
| item_name | string(200) | NO | Denormalized item name |
| quantity | int | NO | Quantity |
| unit_price | decimal(10,2) | NO | Price per unit |
| total_price | decimal(10,2) | NO | quantity × unit_price |
| paid_by_user_id | string(20) | YES | FK → Users (for split billing) |
| status | enum | NO | UNPAID, PAID, REFUNDED |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 8. Users

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| user_id | string(20) | NO | Primary Key (U001) |
| name | string(200) | NO | Full name |
| phone | string(20) | YES | Phone number |
| email | string(255) | YES | Email address |
| auth_provider | string(50) | YES | google, email_otp |
| auth_id | string(255) | YES | Provider-specific ID |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 9. TeamMembers

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| member_id | string(20) | NO | Primary Key (TM001) |
| business_id | string(20) | NO | FK → Businesses |
| user_id | string(20) | NO | FK → Users |
| role | enum | NO | ADMIN, STAFF |
| status | string(20) | NO | ACTIVE, INACTIVE |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |

---

## 10. Addresses

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| address_id | string(20) | NO | Primary Key (ADDR001) |
| user_id | string(20) | NO | FK → Users |
| type | string(20) | NO | HOME, WORK, OTHER |
| address_line1 | string(500) | NO | Street address |
| city | string(100) | NO | City name |
| pincode | string(20) | NO | Postal code |
| lat_long | string(50) | YES | GPS coordinates |

---

## 11. FAQ

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| business_id | string(20) | NO | FK → Businesses |
| question | text | NO | FAQ question |
| answer | text | NO | FAQ answer |
| created_at | datetime | NO | Record created |
| updated_at | datetime | YES | Record updated |
