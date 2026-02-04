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

export interface Business {
  id: string
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
  id: string
  businessId: string
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
  id: string
  businessId: string
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
  id: string
  businessId: string
  categoryId: string
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
  id: string
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
  id: string
  businessId: string
  userId: string
  role: UserRole
  status: TeamMemberStatus
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  user?: User
  business?: Business
}

export interface Address {
  id: string
  userId: string
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
  id: string
  sessionId: string | null
  deviceId: string | null
  userId: string | null
  businessId: string
  intent: IntentType
  resourceId: string | null
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
  assistantSessionId: string | null
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
  id: string
  cartId: string
  itemId: string
  itemName: string
  quantity: number
  unitPrice: number
  totalPrice: number
  notes: string | null
  status: CartItemStatus
  preparedBy: string | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  menuItem?: MenuItem
  preparedByMember?: TeamMember
}

export interface Bill {
  id: string
  cartId: string
  businessId: string
  subtotal: number
  taxPercent: number
  taxAmount: number
  discountAmount: number
  serviceCharge: number
  totalAmount: number
  paidAmount: number
  balanceDue: number
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
  id: string
  billId: string
  cartItemId: string
  itemName: string
  quantity: number
  unitPrice: number
  totalPrice: number
  paidByUserId: string | null
  status: BillItemStatus
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
  paidByUser?: User
  cartItem?: CartItem
}

export interface FAQ {
  id: string
  businessId: string
  question: string
  answer: string
  isActive: boolean
  createdAt: Date
  updatedAt: Date | null
}

export interface AssistantSession {
  id: string
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
  id: string
  sessionId: string
  role: 'user' | 'assistant'
  content: string
  audioUrl: string | null
  intent: string | null
  entities: Record<string, unknown>
  confidence: number | null
  createdAt: Date
}

export interface Device {
  id: string
  deviceId: string
  name: string | null
  deviceType: DeviceType | null
  location: string | null
  isActive: boolean
  lastSeen: Date | null
  createdAt: Date
  updatedAt: Date | null
}

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
