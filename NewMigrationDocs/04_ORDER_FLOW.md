# Complete Order Flow

## Restaurant Order Lifecycle (Spiceclub/PacDonalds)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           RESTAURANT ORDER LIFECYCLE                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  STEP 1: Customer Entry                                                                 │
│  ════════════════════════                                                               │
│  • Customer scans QR at Table T01                                                       │
│  • Resource T01 status: AVAILABLE → ASSIGNED                                            │
│  • Cart created: CART006 (status: DRAFT)                                                │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Cart: CART006                                                          │            │
│  │  ├─ user_id: U011 (Customer Raj)                                        │            │
│  │  ├─ resource_id: P02                                                    │            │
│  │  ├─ status: DRAFT                                                       │            │
│  │  └─ subtotal: 0                                                         │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
│                                        │                                                │
│                                        ▼                                                │
│                                                                                         │
│  STEP 2: Add Items                                                                      │
│  ═════════════════                                                                      │
│  • Customer adds items via app/voice                                                    │
│  • CartItems created with status: DRAFT                                                 │
│  • Cart subtotal updated                                                                │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Cart: CART006                      CartItems:                          │            │
│  │  ├─ status: DRAFT                   ├─ CI010: Chicken Burger ×2 (DRAFT) │            │
│  │  └─ subtotal: 456                   ├─ CI011: Regular Fries (DRAFT)     │            │
│  │                                     └─ CI012: Coke (DRAFT)              │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
│                                        │                                                │
│                                        ▼                                                │
│                                                                                         │
│  STEP 3: Order Confirmed                                                                │
│  ═══════════════════════                                                                │
│  • Customer clicks "Place Order"                                                        │
│  • Cart status: DRAFT → CONFIRMED                                                       │
│  • All CartItems: DRAFT → PENDING                                                       │
│  • Kitchen gets notified                                                                │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Cart: CART006                      CartItems:                          │            │
│  │  ├─ status: CONFIRMED               ├─ CI010: Chicken Burger (PENDING)  │            │
│  │  └─ subtotal: 456                   ├─ CI011: Regular Fries (PENDING)   │            │
│  │                                     └─ CI012: Coke (PENDING)            │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
│                                        │                                                │
│                                        ▼                                                │
│                                                                                         │
│  STEP 4: Kitchen Processing                                                             │
│  ══════════════════════════                                                             │
│  • Cart status: CONFIRMED → IN_PROGRESS                                                 │
│  • Kitchen picks up items one by one                                                    │
│  • Each CartItem: PENDING → PREPARING → READY                                           │
│  • prepared_by set to staff member                                                      │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Cart: CART006                                                          │            │
│  │  ├─ status: IN_PROGRESS                                                 │            │
│  │  │                                                                      │            │
│  │  │  CartItems:                                                          │            │
│  │  │  ├─ CI010: Chicken Burger → PREPARING (by TM006 Staff Bunty)         │            │
│  │  │  ├─ CI011: Regular Fries  → READY (by TM007 Staff Pinky)             │            │
│  │  │  └─ CI012: Coke           → READY (by TM006 Staff Bunty)             │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
│                                        │                                                │
│                                        ▼                                                │
│                                                                                         │
│  STEP 5: Items Ready & Served                                                           │
│  ═══════════════════════════                                                            │
│  • Each CartItem: READY → SERVED                                                        │
│  • When ALL items SERVED → Cart status: IN_PROGRESS → READY                             │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Cart: CART006                                                          │            │
│  │  ├─ status: READY (waiting for payment)                                 │            │
│  │  │                                                                      │            │
│  │  │  CartItems:                                                          │            │
│  │  │  ├─ CI010: Chicken Burger ×2  → SERVED                               │            │
│  │  │  ├─ CI011: Regular Fries      → SERVED                               │            │
│  │  │  └─ CI012: Coke               → SERVED                               │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
│                                        │                                                │
│                                        ▼                                                │
│                                                                                         │
│  STEP 6: Billing & Payment                                                              │
│  ═════════════════════════                                                              │
│  • Bill generated from Cart                                                             │
│  • BillItems created from CartItems                                                     │
│  • Customer pays → Bill status: PENDING → PAID                                          │
│  • Cart status: READY → COMPLETED                                                       │
│  • Resource released: P02 status: ASSIGNED → AVAILABLE                                  │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐            │
│  │  Bills: BILL003                      BillItems:                         │            │
│  │  ├─ cart_id: CART006                 ├─ BI00X: Chicken Burger (PAID)    │            │
│  │  ├─ subtotal: 456                    ├─ BI00X: Regular Fries (PAID)     │            │
│  │  ├─ tax (5%): 24                     └─ BI00X: Coke (PAID)              │            │
│  │  ├─ total: 500                                                          │            │
│  │  ├─ paid: 500                                                           │            │
│  │  └─ status: PAID                                                        │            │
│  └─────────────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Split Billing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     SPLIT BILLING FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Group of 3 friends at table → Cart with 5 items                │
│                                                                 │
│  Bill generated:                                                │
│  ├─ BI001: Chicken Burger ×2 → ₹338                             │
│  ├─ BI002: Veg Burger        → ₹129                             │
│  ├─ BI003: Large Fries       → ₹119                             │
│  ├─ BI004: Coke ×2           → ₹118                             │
│  └─ BI005: Chocolate Shake   → ₹129                             │
│                                                                 │
│  Friend A pays for BI001, BI004:                                │
│  └─ BI001, BI004 → paid_by_user_id: U011, status: PAID          │
│                                                                 │
│  Friend B pays for BI002, BI003:                                │
│  └─ BI002, BI003 → paid_by_user_id: U012, status: PAID          │
│                                                                 │
│  Friend C pays for BI005:                                       │
│  └─ BI005 → paid_by_user_id: U013, status: PAID                 │
│                                                                 │
│  All BillItems PAID → Bill status: PAID                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Bill Calculation Formula

```
subtotal       = SUM(CartItems.total_price)
tax_amount     = subtotal × (tax_percent / 100)
total_amount   = subtotal + tax_amount - discount_amount + service_charge
balance_due    = total_amount - paid_amount

Bill.status:
  - PENDING  : paid_amount = 0
  - PARTIAL  : paid_amount > 0 AND paid_amount < total_amount  
  - PAID     : paid_amount >= total_amount
```
