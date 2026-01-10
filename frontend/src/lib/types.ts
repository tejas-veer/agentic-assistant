export type OrderStatus = 
  | 'pending'
  | 'confirmed'
  | 'preparing'
  | 'ready'
  | 'completed'
  | 'cancelled'

export type PaymentStatus = 
  | 'pending'
  | 'paid'
  | 'failed'
  | 'refunded'

export type AssistantType = 
  | 'voice'
  | 'kiosk'
  | 'call'

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
  items?: import('./api').MenuItem[]
  cartItems?: { name: string; quantity: number; price: number }[]
  cartTotal?: number
  orderNumber?: string
  suggestions?: string[]
}

export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: MessageContent[]
  timestamp?: Date
}

