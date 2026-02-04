# Entity Relationship Diagram (Merged Schema)

> **Updated:** UUID (String 36) primary keys for all tables

## Mermaid ER Diagram

```mermaid
erDiagram
    Businesses {
        uuid id PK
        string name
        string type
        string intents
        boolean requires_approval
        string payment_flow
        string payment_modes
        string resource_type
        string contact_phone
        string timings
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Resources {
        uuid id PK
        uuid business_id FK
        string type
        string name
        int capacity
        json meta_json
        string status
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Categories {
        uuid id PK
        uuid business_id FK
        string name
        string description
        string image_url
        int display_order
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Menu {
        uuid id PK
        uuid business_id FK
        uuid category_id FK
        string name
        string description
        decimal price
        string image_url
        boolean available
        int quantity
        int preparation_time_mins
        int display_order
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    FAQ {
        uuid id PK
        uuid business_id FK
        string question
        string answer
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Users {
        uuid id PK
        string name
        string phone
        string email
        string hashed_password
        string auth_provider
        string auth_id
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    TeamMembers {
        uuid id PK
        uuid business_id FK
        uuid user_id FK
        string role
        string status
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Addresses {
        uuid id PK
        uuid user_id FK
        string type
        string address_line1
        string city
        string pincode
        string lat_long
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Cart {
        uuid id PK
        string session_id
        string device_id
        uuid user_id FK
        uuid business_id FK
        string intent
        uuid resource_id FK
        string customer_name
        string customer_phone
        int item_count
        decimal subtotal
        decimal tax
        decimal total
        string status
        string source
        string notes
        int estimated_ready_time
        uuid assistant_session_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CartItems {
        uuid id PK
        uuid cart_id FK
        uuid item_id FK
        string item_name
        int quantity
        decimal unit_price
        decimal total_price
        string notes
        string status
        uuid prepared_by FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Bills {
        uuid id PK
        uuid cart_id FK
        uuid business_id FK
        decimal subtotal
        decimal tax_percent
        decimal tax_amount
        decimal discount_amount
        decimal service_charge
        decimal total_amount
        decimal paid_amount
        string payment_mode
        string status
        string payment_ref
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    BillItems {
        uuid id PK
        uuid bill_id FK
        uuid cart_item_id FK
        string item_name
        int quantity
        decimal unit_price
        decimal total_price
        uuid paid_by_user_id FK
        string status
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    AssistantSessions {
        uuid id PK
        string session_id UK
        string assistant_type
        string device_id
        string phone_number
        string status
        json context
        datetime started_at
        datetime ended_at
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ConversationMessages {
        uuid id PK
        uuid session_id FK
        string role
        string content
        string audio_url
        string intent
        json entities
        decimal confidence
        datetime created_at
    }

    Devices {
        uuid id PK
        string device_id UK
        string name
        string device_type
        string location
        boolean is_active
        datetime last_seen
        datetime created_at
        datetime updated_at
    }

    Businesses ||--o{ Resources : "has"
    Businesses ||--o{ Categories : "has"
    Businesses ||--o{ Menu : "offers"
    Businesses ||--o{ FAQ : "has"
    Businesses ||--o{ TeamMembers : "employs"
    Businesses ||--o{ Cart : "receives"
    Businesses ||--o{ Bills : "generates"

    Categories ||--o{ Menu : "contains"

    Users ||--o{ Addresses : "has"
    Users ||--o{ Cart : "creates"
    Users ||--o{ TeamMembers : "member_of"
    Users ||--o{ BillItems : "pays"

    Resources ||--o{ Cart : "assigned_to"
    Menu ||--o{ CartItems : "added_as"

    Cart ||--o{ CartItems : "contains"
    Cart ||--|| Bills : "generates"

    Bills ||--o{ BillItems : "itemized"
    CartItems ||--o{ BillItems : "billed"

    TeamMembers ||--o{ CartItems : "prepares"

    AssistantSessions ||--o{ Cart : "creates"
    AssistantSessions ||--o{ ConversationMessages : "contains"
```

---

## Relationships Text Format

```
BUSINESS CONTEXT
════════════════
Businesses (1) ──── (N) Resources
Businesses (1) ──── (N) Categories
Businesses (1) ──── (N) Menu
Businesses (1) ──── (N) FAQ
Businesses (1) ──── (N) TeamMembers
Businesses (1) ──── (N) Cart
Businesses (1) ──── (N) Bills

MENU STRUCTURE
══════════════
Categories (1) ──── (N) Menu

USER CONTEXT
════════════
Users (1) ──── (N) Addresses
Users (1) ──── (N) Cart
Users (1) ──── (N) TeamMembers
Users (1) ──── (N) BillItems (paid_by)

ORDER FLOW
══════════
Resources (1) ──── (N) Cart
Cart (1) ──── (N) CartItems
Cart (1) ──── (1) Bills
Menu (1) ──── (N) CartItems
Bills (1) ──── (N) BillItems
CartItems (1) ──── (N) BillItems
TeamMembers (1) ──── (N) CartItems (prepared_by)

ASSISTANT CONTEXT (EXISTING)
════════════════════════════
AssistantSessions (1) ──── (N) Cart
AssistantSessions (1) ──── (N) ConversationMessages
```

---

## Tables Summary (15 Total)

| # | Table | Type | PK Type | FK References |
|---|-------|------|---------|---------------|
| 1 | Businesses | NEW | UUID | - |
| 2 | Resources | NEW | UUID | business_id |
| 3 | Categories | EXISTING+ENHANCED | UUID | business_id |
| 4 | Menu | MERGED | UUID | business_id, category_id |
| 5 | Users | MERGED | UUID | - |
| 6 | TeamMembers | NEW | UUID | business_id, user_id |
| 7 | Addresses | NEW+ENHANCED | UUID | user_id |
| 8 | Cart | MERGED | UUID | user_id, business_id, resource_id, assistant_session_id |
| 9 | CartItems | NEW | UUID | cart_id, item_id, prepared_by |
| 10 | Bills | NEW | UUID | cart_id, business_id |
| 11 | BillItems | NEW | UUID | bill_id, cart_item_id, paid_by_user_id |
| 12 | FAQ | NEW | UUID | business_id |
| 13 | AssistantSessions | EXISTING | UUID | - |
| 14 | ConversationMessages | EXISTING | UUID | session_id |
| 15 | Devices | EXISTING | UUID | - |
