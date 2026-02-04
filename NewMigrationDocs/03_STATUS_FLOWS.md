# Status Flow Diagrams

## 1. Cart Status Flow

```mermaid
stateDiagram-v2
    [*] --> DRAFT: User starts adding items
    DRAFT --> CONFIRMED: User places order
    DRAFT --> ABANDONED: User leaves
    CONFIRMED --> IN_PROGRESS: Kitchen starts
    CONFIRMED --> CANCELLED: Order cancelled
    IN_PROGRESS --> READY: All items ready
    READY --> COMPLETED: Bill paid
    COMPLETED --> [*]
    ABANDONED --> [*]
    CANCELLED --> [*]
```

### Cart Status Definitions

| Status | Description | Next Actions |
|--------|-------------|--------------|
| `DRAFT` | User is browsing, adding items | CONFIRMED, ABANDONED |
| `CONFIRMED` | Order placed, sent to kitchen | IN_PROGRESS, CANCELLED |
| `IN_PROGRESS` | Kitchen preparing items | READY |
| `READY` | All items ready for serving | COMPLETED |
| `COMPLETED` | Order finished, bill paid | - |
| `ABANDONED` | User left without ordering | - |
| `CANCELLED` | Order was cancelled | - |

---

## 2. CartItem Status Flow

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Item added to cart
    DRAFT --> PENDING: Order confirmed
    DRAFT --> ABANDONED: Cart abandoned
    PENDING --> PREPARING: Kitchen picks up
    PENDING --> CANCELLED: Item cancelled
    PREPARING --> READY: Item cooked
    READY --> SERVED: Delivered to table
    SERVED --> [*]
    ABANDONED --> [*]
    CANCELLED --> [*]
```

### CartItem Status Definitions

| Status | Description | Who Updates |
|--------|-------------|-------------|
| `DRAFT` | Item in cart, not yet ordered | System |
| `PENDING` | Order confirmed, waiting for kitchen | System |
| `PREPARING` | Kitchen is cooking this item | Staff |
| `READY` | Item is cooked, ready to serve | Staff |
| `SERVED` | Item delivered to customer | Staff |
| `ABANDONED` | Cart was abandoned | System |
| `CANCELLED` | Item was cancelled | Admin |

---

## 3. Bill Status Flow

```mermaid
stateDiagram-v2
    [*] --> PENDING: Bill generated
    PENDING --> PARTIAL: Partial payment
    PENDING --> PAID: Full payment
    PARTIAL --> PAID: Remaining paid
    PAID --> REFUNDED: Refund issued
    PAID --> [*]
    REFUNDED --> [*]
```

### Bill Status Definitions

| Status | Condition |
|--------|-----------|
| `PENDING` | paid_amount = 0 |
| `PARTIAL` | 0 < paid_amount < total_amount |
| `PAID` | paid_amount >= total_amount |
| `REFUNDED` | Refund processed |

---

## 4. BillItem Status Flow

```mermaid
stateDiagram-v2
    [*] --> UNPAID: Bill item created
    UNPAID --> PAID: Payment received
    PAID --> REFUNDED: Refund issued
    PAID --> [*]
    REFUNDED --> [*]
```

---

## 5. Resource Status Flow

```mermaid
stateDiagram-v2
    [*] --> AVAILABLE: Table/Room free
    AVAILABLE --> ASSIGNED: Customer seated
    ASSIGNED --> AVAILABLE: Customer leaves
```

### Resource Status Definitions

| Status | Description |
|--------|-------------|
| `AVAILABLE` | Resource is free for use |
| `ASSIGNED` | Resource is occupied by a customer |

---

## Status Sync Rules

### When Cart Status Changes

| Cart Status | CartItems Status | Resource Status |
|-------------|------------------|-----------------|
| DRAFT → CONFIRMED | DRAFT → PENDING | - |
| CONFIRMED → IN_PROGRESS | (individual) | - |
| READY → COMPLETED | (all SERVED) | ASSIGNED → AVAILABLE |
| DRAFT → ABANDONED | DRAFT → ABANDONED | - |
| CONFIRMED → CANCELLED | PENDING → CANCELLED | ASSIGNED → AVAILABLE |

### Parent-Child Status Derivation

```
Cart.status = derive_from(CartItems[].status)

If ALL items DRAFT       → Cart = DRAFT
If ALL items PENDING     → Cart = CONFIRMED
If ANY item PREPARING    → Cart = IN_PROGRESS
If ALL items READY/SERVED → Cart = READY
If ALL items SERVED      → Cart = COMPLETED (after payment)
```
