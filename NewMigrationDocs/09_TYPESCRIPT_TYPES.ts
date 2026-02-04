/**
 * TypeScript Types for the new schema
 * Copy this to: frontend/src/lib/types.ts
 */

// ==================== ENUMS ====================

export type BusinessType = 'restaurant' | 'hotel' | 'clinic'

export type PaymentFlow = 'pre_service' | 'post_service'

export type ResourceType = 'table' | 'room' | 'slot'

export type ResourceStatus = 'available' | 'assigned'

export type CartStatus = 
  | 'draft'
  | 'confirmed'
  | 'in_progress'
  | 'ready'
  | 'completed'
  | 'abandoned'
  | 'cancelled'

export type CartItemStatus = 
  | 'draft'
  | 'pending'
  | 'preparing'
  | 'ready'
  | 'served'
  | 'abandoned'
  | 'cancelled'

export type BillStatus = 
  | 'pending'
  | 'partial'
  | 'paid'
  | 'refunded'

export type BillItemStatus = 
  | 'unpaid'
  | 'paid'
  | 'refunded'

export type PaymentMethod = 'cash' | 'upi' | 'card'

export type UserRole = 'admin' | 'staff'

export type OrderSource = 'app' | 'voice' | 'chat'

export type IntentType = 'food_order' | 'booking' | 'appointment'

// ==================== INTERFACES ====================

export interface Business {
  id: string
  businessId: string
  name: string
  type: BusinessType
  intents: string
  requiresApproval: boolean
  paymentFlow: PaymentFlow
  paymentModes: string
  resourceType: ResourceType
  contactPhone: string
  timings: string
  createdAt: Date
  updatedAt: Date
}

export interface Resource {
  id: string
  resourceId: string
  businessId: string
  type: ResourceType
  name: string
  capacity: number
  metaJson: Record<string, unknown>
  status: ResourceStatus
  createdAt: Date
  updatedAt: Date
}

export interface MenuItem {
  id: string
  itemId: string
  businessId: string
  name: string
  category: string
  price: number
  available: boolean
  quantity: number
  description: string
  createdAt: Date
  updatedAt: Date
}

export interface User {
  id: string
  userId: string
  name: string
  phone: string
  email: string
  authProvider: string
  authId: string
  createdAt: Date
  updatedAt: Date
}

export interface TeamMember {
  id: string
  memberId: string
  businessId: string
  userId: string
  role: UserRole
  status: string
  createdAt: Date
  updatedAt: Date
  // Joined data
  user?: User
}

export interface Address {
  id: string
  addressId: string
  userId: string
  type: 'home' | 'work' | 'other'
  addressLine1: string
  city: string
  pincode: string
  latLong: string
}

export interface Cart {
  id: string
  cartId: string
  userId: string | null
  businessId: string
  intent: IntentType
  resourceId: string | null
  customerName: string
  customerPhone: string
  itemCount: number
  subtotal: number
  status: CartStatus
  source: OrderSource
  createdAt: Date
  updatedAt: Date
  // Joined data
  items?: CartItem[]
  resource?: Resource
  bill?: Bill
}

export interface CartItem {
  id: string
  cartItemId: string
  cartId: string
  itemId: string
  itemName: string
  quantity: number
  unitPrice: number
  totalPrice: number
  notes: string
  status: CartItemStatus
  preparedBy: string | null
  createdAt: Date
  updatedAt: Date
  // Joined data
  menuItem?: MenuItem
  preparedByMember?: TeamMember
}

export interface Bill {
  id: string
  billId: string
  cartId: string
  businessId: string
  subtotal: number
  taxPercent: number
  taxAmount: number
  discountAmount: number
  serviceCharge: number
  totalAmount: number
  paidAmount: number
  paymentMode: PaymentMethod | null
  status: BillStatus
  paymentRef: string
  createdAt: Date
  updatedAt: Date
  // Joined data
  items?: BillItem[]
}

export interface BillItem {
  id: string
  billItemId: string
  billId: string
  cartItemId: string
  itemName: string
  quantity: number
  unitPrice: number
  totalPrice: number
  paidByUserId: string | null
  status: BillItemStatus
  createdAt: Date
  updatedAt: Date
  // Joined data
  paidByUser?: User
}

export interface FAQ {
  id: string
  businessId: string
  question: string
  answer: string
  createdAt: Date
  updatedAt: Date
}

// ==================== API TYPES ====================

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// ==================== REQUEST TYPES ====================

export interface AddToCartRequest {
  cartId: string
  itemId: string
  quantity: number
  notes?: string
}

export interface UpdateCartItemRequest {
  cartItemId: string
  quantity?: number
  notes?: string
}

export interface ConfirmOrderRequest {
  cartId: string
  customerName?: string
  customerPhone?: string
}

export interface UpdateCartItemStatusRequest {
  cartItemId: string
  status: CartItemStatus
  preparedBy?: string
}

export interface ProcessPaymentRequest {
  billId: string
  amount: number
  paymentMode: PaymentMethod
  paymentRef?: string
}

export interface SplitPaymentRequest {
  billId: string
  billItemIds: string[]
  paidByUserId: string
  amount: number
  paymentMode: PaymentMethod
}
