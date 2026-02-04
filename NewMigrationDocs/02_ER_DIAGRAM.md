# Entity Relationship Diagram

## Mermaid ER Diagram

```mermaid
erDiagram
    Businesses {
        string business_id PK
        string name
        string type
        string intents
        boolean requires_approval
        string payment_flow
        string payment_modes
        string resource_type
        string contact_phone
        string timings
        datetime created_at
        datetime updated_at
    }

    Resources {
        string resource_id PK
        string business_id FK
        string type
        string name
        int capacity
        json meta_json
        string status
        datetime created_at
        datetime updated_at
    }

    Menu {
        string item_id PK
        string business_id FK
        string name
        string category
        decimal price
        boolean available
        int quantity
        string description
        datetime created_at
        datetime updated_at
    }

    FAQ {
        string id PK
        string business_id FK
        string question
        string answer
        datetime created_at
        datetime updated_at
    }

    Users {
        string user_id PK
        string name
        string phone
        string email
        string auth_provider
        string auth_id
        datetime created_at
        datetime updated_at
    }

    TeamMembers {
        string member_id PK
        string business_id FK
        string user_id FK
        string role
        string status
        datetime created_at
        datetime updated_at
    }

    Addresses {
        string address_id PK
        string user_id FK
        string type
        string address_line1
        string city
        string pincode
        string lat_long
    }

    Cart {
        string cart_id PK
        string user_id FK
        string business_id FK
        string intent
        string resource_id FK
        string customer_name
        string customer_phone
        int item_count
        decimal subtotal
        string status
        string source
        datetime created_at
        datetime updated_at
    }

    CartItems {
        string cart_item_id PK
        string cart_id FK
        string item_id FK
        string item_name
        int quantity
        decimal unit_price
        decimal total_price
        string notes
        string status
        string prepared_by FK
        datetime created_at
        datetime updated_at
    }

    Bills {
        string bill_id PK
        string cart_id FK
        string business_id FK
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
        datetime created_at
        datetime updated_at
    }

    BillItems {
        string bill_item_id PK
        string bill_id FK
        string cart_item_id FK
        string item_name
        int quantity
        decimal unit_price
        decimal total_price
        string paid_by_user_id FK
        string status
        datetime created_at
        datetime updated_at
    }

    Businesses ||--o{ Resources : "has"
    Businesses ||--o{ Menu : "offers"
    Businesses ||--o{ FAQ : "has"
    Businesses ||--o{ TeamMembers : "employs"
    Businesses ||--o{ Cart : "receives"
    Businesses ||--o{ Bills : "generates"

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
```

---

## Relationships Text Format

```
Businesses (1) ──── (N) Resources
Businesses (1) ──── (N) Menu
Businesses (1) ──── (N) FAQ
Businesses (1) ──── (N) TeamMembers
Businesses (1) ──── (N) Cart
Businesses (1) ──── (N) Bills

Users (1) ──── (N) Addresses
Users (1) ──── (N) Cart
Users (1) ──── (N) TeamMembers
Users (1) ──── (N) BillItems (paid_by)

Resources (1) ──── (N) Cart

Cart (1) ──── (N) CartItems
Cart (1) ──── (1) Bills

Menu (1) ──── (N) CartItems

Bills (1) ──── (N) BillItems
CartItems (1) ──── (N) BillItems

TeamMembers (1) ──── (N) CartItems (prepared_by)
```
