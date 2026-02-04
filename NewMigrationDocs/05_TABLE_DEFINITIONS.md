# Table Definitions (Merged Schema)

> **Updated:** Standard integer PKs and FKs. Removed string-based readable IDs.

---

## 1. Businesses (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| name | string(200) | NO | - | Business name |
| type | enum | NO | - | RESTAURANT, HOTEL, CLINIC |
| intents | string(100) | YES | - | FOOD_ORDER, BOOKING, APPOINTMENT |
| requires_approval | boolean | NO | true | Whether orders need admin approval |
| payment_flow | enum | NO | post_service | PRE_SERVICE, POST_SERVICE |
| payment_modes | string(100) | YES | - | CASH,UPI,CARD |
| resource_type | enum | YES | - | TABLE, ROOM, SLOT |
| contact_phone | string(20) | YES | - | Business contact |
| timings | string(100) | YES | - | Operating hours |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 2. Resources (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| business_id | int | NO | - | FK → Businesses.id |
| type | enum | NO | - | TABLE, ROOM, SLOT |
| name | string(200) | NO | - | Display name |
| capacity | int | NO | 1 | Max guests |
| meta_json | json | YES | {} | {location, ac, floor, view} |
| status | enum | NO | available | AVAILABLE, ASSIGNED |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 3. Categories (EXISTING - ENHANCED)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| business_id | int | NO | - | FK → Businesses.id (NEW) |
| name | string(100) | NO | - | Category name |
| description | text | YES | - | Category description |
| image_url | string(500) | YES | - | Category image |
| display_order | int | NO | 0 | Sort order |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 4. Menu (MERGED)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| business_id | int | NO | - | FK → Businesses.id |
| category_id | int | NO | - | FK → Categories.id |
| name | string(200) | NO | - | Item name |
| description | text | YES | - | Item description |
| price | decimal(10,2) | NO | - | Item price |
| image_url | string(500) | YES | - | Item image |
| available | boolean | NO | true | Is item available |
| quantity | int | YES | 100 | Stock quantity |
| preparation_time_mins | int | NO | 10 | ETA in minutes |
| display_order | int | NO | 0 | Sort order within category |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 5. Users (MERGED)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| name | string(200) | NO | - | Full name |
| phone | string(20) | YES | - | Phone number |
| email | string(255) | YES | - | Email address |
| hashed_password | string(255) | YES | - | Password hash |
| auth_provider | string(50) | YES | - | google, email_otp |
| auth_id | string(255) | YES | - | Provider-specific ID |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 6. TeamMembers (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| business_id | int | NO | - | FK → Businesses.id |
| user_id | int | NO | - | FK → Users.id |
| role | enum | NO | staff | ADMIN, STAFF |
| status | string(20) | NO | active | ACTIVE, INACTIVE |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 7. Addresses (NEW - ENHANCED)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| user_id | int | NO | - | FK → Users.id |
| type | string(20) | NO | - | HOME, WORK, OTHER |
| address_line1 | string(500) | NO | - | Street address |
| city | string(100) | NO | - | City name |
| pincode | string(20) | NO | - | Postal code |
| lat_long | string(50) | YES | - | GPS coordinates |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 8. Cart (MERGED)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| session_id | string(100) | YES | - | Browser session |
| device_id | string(100) | YES | - | Kiosk device ID |
| user_id | int | YES | - | FK → Users.id (nullable for guests) |
| business_id | int | NO | - | FK → Businesses.id |
| intent | enum | NO | food_order | FOOD_ORDER, BOOKING, APPOINTMENT |
| resource_id | int | YES | - | FK → Resources.id |
| customer_name | string(200) | YES | - | Customer name |
| customer_phone | string(20) | YES | - | Customer phone |
| item_count | int | NO | 0 | Total items count |
| subtotal | decimal(10,2) | NO | 0 | Sum of CartItems.total_price |
| tax | decimal(10,2) | NO | 0 | Tax amount |
| total | decimal(10,2) | NO | 0 | Total with tax |
| status | enum | NO | draft | DRAFT, CONFIRMED, IN_PROGRESS, READY, COMPLETED, ABANDONED, CANCELLED |
| source | enum | NO | app | APP, VOICE, CHAT |
| notes | text | YES | - | Order notes |
| estimated_ready_time | int | YES | - | ETA in minutes |
| assistant_session_id | int | YES | - | FK → AssistantSessions.id |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 9. CartItems (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| cart_id | int | NO | - | FK → Cart.id |
| item_id | int | NO | - | FK → Menu.id |
| item_name | string(200) | NO | - | Denormalized item name |
| quantity | int | NO | 1 | Quantity ordered |
| unit_price | decimal(10,2) | NO | - | Price per unit |
| total_price | decimal(10,2) | NO | - | quantity × unit_price |
| notes | text | YES | - | Special instructions |
| status | enum | NO | draft | DRAFT, PENDING, PREPARING, READY, SERVED, ABANDONED, CANCELLED |
| prepared_by | int | YES | - | FK → TeamMembers.id |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 10. Bills (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| cart_id | int | NO | - | FK → Cart.id |
| business_id | int | NO | - | FK → Businesses.id |
| subtotal | decimal(10,2) | NO | 0 | Sum before tax |
| tax_percent | decimal(5,2) | NO | 0 | Tax percentage |
| tax_amount | decimal(10,2) | NO | 0 | Calculated tax |
| discount_amount | decimal(10,2) | NO | 0 | Discount applied |
| service_charge | decimal(10,2) | NO | 0 | Service charge |
| total_amount | decimal(10,2) | NO | 0 | Final amount |
| paid_amount | decimal(10,2) | NO | 0 | Amount paid |
| payment_mode | enum | YES | - | CASH, UPI, CARD |
| status | enum | NO | pending | PENDING, PARTIAL, PAID, REFUNDED |
| payment_ref | string(100) | YES | - | Payment reference |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 11. BillItems (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| bill_id | int | NO | - | FK → Bills.id |
| cart_item_id | int | NO | - | FK → CartItems.id |
| item_name | string(200) | NO | - | Denormalized item name |
| quantity | int | NO | 1 | Quantity |
| unit_price | decimal(10,2) | NO | - | Price per unit |
| total_price | decimal(10,2) | NO | - | quantity × unit_price |
| paid_by_user_id | int | YES | - | FK → Users.id (for split billing) |
| status | enum | NO | unpaid | UNPAID, PAID, REFUNDED |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 12. FAQ (NEW)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| business_id | int | NO | - | FK → Businesses.id |
| question | text | NO | - | FAQ question |
| answer | text | NO | - | FAQ answer |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 13. AssistantSessions (EXISTING - KEPT)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| session_id | string(100) | NO | - | Unique session identifier |
| assistant_type | enum | NO | - | VOICE, CALL, CHAT |
| device_id | string(100) | YES | - | Associated device |
| phone_number | string(20) | YES | - | For call type |
| status | enum | NO | active | ACTIVE, COMPLETED, ABANDONED |
| context | json | NO | {} | Conversation context |
| started_at | datetime | NO | now | Session start |
| ended_at | datetime | YES | - | Session end |
| is_active | boolean | NO | true | Soft delete flag |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## 14. ConversationMessages (EXISTING - KEPT)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| session_id | int | NO | - | FK → AssistantSessions.id |
| role | string(20) | NO | - | user, assistant |
| content | text | NO | - | Message content |
| audio_url | string(500) | YES | - | Audio file URL |
| intent | string(100) | YES | - | Detected intent |
| entities | json | NO | {} | Extracted entities |
| confidence | decimal(5,4) | YES | - | Confidence score |
| created_at | datetime | NO | now | Record created |

---

## 15. Devices (EXISTING - KEPT)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | int | NO | auto | Primary Key |
| device_id | string(100) | NO | - | Unique device identifier |
| name | string(200) | YES | - | Device name |
| device_type | string(20) | YES | - | KIOSK, TABLET, WEB, PHONE |
| location | string(200) | YES | - | Physical location |
| is_active | boolean | NO | true | Soft delete flag |
| last_seen | datetime | YES | - | Last activity |
| created_at | datetime | NO | now | Record created |
| updated_at | datetime | YES | - | Record updated |

---

## Table Summary

| # | Table | Type | FK References |
|---|-------|------|---------------|
| 1 | Businesses | NEW | - |
| 2 | Resources | NEW | business_id |
| 3 | Categories | EXISTING+ENHANCED | business_id |
| 4 | Menu | MERGED | business_id, category_id |
| 5 | Users | MERGED | - |
| 6 | TeamMembers | NEW | business_id, user_id |
| 7 | Addresses | NEW+ENHANCED | user_id |
| 8 | Cart | MERGED | user_id, business_id, resource_id, assistant_session_id |
| 9 | CartItems | NEW | cart_id, item_id, prepared_by |
| 10 | Bills | NEW | cart_id, business_id |
| 11 | BillItems | NEW | bill_id, cart_item_id, paid_by_user_id |
| 12 | FAQ | NEW | business_id |
| 13 | AssistantSessions | EXISTING | - |
| 14 | ConversationMessages | EXISTING | session_id |
| 15 | Devices | EXISTING | - |
