/**
 * TypeScript Types for the merged schema
 * Copy this to: frontend/src/lib/types.ts
 *
 * Standard integer PKs and FKs (no string-based readable IDs)
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

export type AssistantType = 'voice' | 'call' | 'chat'

export type ConversationStatus = 'active' | 'completed' | 'abandoned'

export type DeviceType = 'kiosk' | 'tablet' | 'web' | 'phone'

export type AddressType = 'home' | 'work' | 'other'

export type TeamMemberStatus = 'active' | 'inactive'

// ==================== INTERFACES ====================

export interface Business {
  id: number
  name: string
  type: BusinessType
  intents: string | null
  requiresApproval: boolean
  paymentFlow: PaymentFlow
  paymentModes: string | null
  resourceType: ResourceType | null
  contactPhone: string | null
  timings: string | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
}

export interface Resource {
  id: number
  businessId: number
  type: ResourceType
  name: string
  capacity: number
  metaJson: Record<string, unknown>
  status: ResourceStatus
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
}

export interface Category {
  id: number
  businessId: number
  name: string
  description: string | null
  imageUrl: string | null
  displayOrder: number
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  items?: MenuItem[]
}

export interface MenuItem {
  id: number
  businessId: number
  categoryId: number
  name: string
  description: string | null
  price: number
  imageUrl: string | null
  available: boolean
  quantity: number
  preparationTimeMins: number
  displayOrder: number
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  category?: Category
}

export interface User {
  id: number
  name: string
  phone: string | null
  email: string | null
  authProvider: string | null
  authId: string | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
}

export interface TeamMember {
  id: number
  businessId: number
  userId: number
  role: UserRole
  status: TeamMemberStatus
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  user?: User
  business?: Business
}

export interface Address {
  id: number
  userId: number
  type: AddressType
  addressLine1: string
  city: string
  pincode: string
  latLong: string | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
}

export interface Cart {
  id: number
  sessionId: string | null
  deviceId: string | null
  userId: number | null
  businessId: number
  intent: IntentType
  resourceId: number | null
  customerName: string | null
  customerPhone: string | null
  itemCount: number
  subtotal: number
  tax: number
  total: number
  status: CartStatus
  source: OrderSource
  notes: string | null
  estimatedReadyTime: number | null
  assistantSessionId: number | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  items?: CartItem[]
  resource?: Resource
  bill?: Bill
  business?: Business
  user?: User
}

export interface CartItem {
  id: number
  cartId: number
  itemId: number
  itemName: string
  quantity: number
  unitPrice: number
  totalPrice: number
  notes: string | null
  status: CartItemStatus
  preparedBy: number | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  menuItem?: MenuItem
  preparedByMember?: TeamMember
}

export interface Bill {
  id: number
  cartId: number
  businessId: number
  subtotal: number
  taxPercent: number
  taxAmount: number
  discountAmount: number
  serviceCharge: number
  totalAmount: number
  paidAmount: number
  paymentMode: PaymentMethod | null
  status: BillStatus
  paymentRef: string | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  items?: BillItem[]
  cart?: Cart
}

export interface BillItem {
  id: number
  billId: number
  cartItemId: number
  itemName: string
  quantity: number
  unitPrice: number
  totalPrice: number
  paidByUserId: number | null
  status: BillItemStatus
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  paidByUser?: User
  cartItem?: CartItem
}

export interface FAQ {
  id: number
  businessId: number
  question: string
  answer: string
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
}

export interface AssistantSession {
  id: number
  sessionId: string
  assistantType: AssistantType
  deviceId: string | null
  phoneNumber: string | null
  status: ConversationStatus
  context: Record<string, unknown>
  startedAt: Date
  endedAt: Date | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  messages?: ConversationMessage[]
}

export interface ConversationMessage {
  id: number
  sessionId: number
  role: 'user' | 'assistant'
  content: string
  audioUrl: string | null
  intent: string | null
  entities: Record<string, unknown>
  confidence: number | null
  createdAt: Date
}

export interface Device {
  id: number
  deviceId: string
  name: string | null
  deviceType: DeviceType | null
  location: string | null
  isActive: boolean
  lastSeen: Date | null
  createdAt: Date
  updatedAt: Date | null
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

export interface CreateCartRequest {
  businessId: number
  sessionId?: string
  deviceId?: string
  userId?: number
  resourceId?: number
  customerName?: string
  customerPhone?: string
  source?: OrderSource
}

export interface AddToCartRequest {
  cartId: number
  itemId: number
  quantity: number
  notes?: string
}

export interface UpdateCartItemRequest {
  cartItemId: number
  quantity?: number
  notes?: string
}

export interface ConfirmOrderRequest {
  cartId: number
  customerName?: string
  customerPhone?: string
  resourceId?: number
}

export interface UpdateCartItemStatusRequest {
  cartItemId: number
  status: CartItemStatus
  preparedBy?: number
}

export interface CreateBillRequest {
  cartId: number
  taxPercent?: number
  discountAmount?: number
  serviceCharge?: number
}

export interface ProcessPaymentRequest {
  billId: number
  amount: number
  paymentMode: PaymentMethod
  paymentRef?: string
}

export interface SplitPaymentRequest {
  billId: number
  billItemIds: number[]
  paidByUserId: number
  amount: number
  paymentMode: PaymentMethod
}

// ==================== MESSAGE CONTENT TYPES (FOR ASSISTANT) ====================

export interface MessageContent {
  type: 'text' | 'menu-items' | 'cart-summary' | 'order-confirmed' | 'suggestions'
  text?: string
  items?: MenuItem[]
  cartItems?: { name: string; quantity: number; price: number }[]
  cartTotal?: number
  orderNumber?: string
  suggestions?: string[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: MessageContent[]
  timestamp?: Date
}
