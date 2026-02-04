import axios from 'axios'
import type { Cart, CartItem, Bill, Category, MenuItem, CartStatus, CartItemStatus, PaymentMethod, ApiResponse, Business, Resource } from './types'
import { DEFAULT_BUSINESS_ID } from './store'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const method = config.method?.toUpperCase()
    const url = config.url
    console.log(`🚀 [API] ${method} ${url}`)
    if (config.data) {
      console.log('📤 Request Body:', JSON.stringify(config.data, null, 2))
    }
    if (config.params) {
      console.log('📤 Request Params:', config.params)
    }
    return config
  },
  (error) => {
    console.error('❌ [API] Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase()
    const url = response.config.url
    console.log(`✅ [API] ${method} ${url} - Status: ${response.status}`)
    console.log('📥 Response:', JSON.stringify(response.data, null, 2))
    return response
  },
  (error) => {
    const method = error.config?.method?.toUpperCase()
    const url = error.config?.url
    console.error(`❌ [API] ${method} ${url} - Error:`, error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export type { MenuItem, Category }

export const menuApi = {
  getMenu: (businessId: string = DEFAULT_BUSINESS_ID) => 
    api.get<ApiResponse<Category[]>>('/menu', { params: { business_id: businessId } }).then(r => r.data.data),
  
  getItem: (itemId: string) =>
    api.get<ApiResponse<MenuItem>>(`/menu/items/${itemId}`).then(r => r.data.data),
  
  searchItems: (businessId: string, q: string) => 
    api.get<ApiResponse<MenuItem[]>>(`/menu/search`, { params: { business_id: businessId, q } }).then(r => r.data.data),
}

export const cartApi = {
  createCart: (data: { businessId: string; sessionId?: string; deviceId?: string }) =>
    api.post<ApiResponse<{ id: string; sessionId: string }>>('/cart', {
      business_id: data.businessId,
      session_id: data.sessionId,
      device_id: data.deviceId
    }).then(r => r.data.data),

  getCart: (cartId: string) => 
    api.get<ApiResponse<Cart | null>>(`/cart/${cartId}`).then(r => r.data.data),
  
  getCartBySession: (sessionId: string) =>
    api.get<ApiResponse<Cart | null>>(`/cart/session/${sessionId}`).then(r => r.data.data),
  
  addItem: (cartId: string, data: { itemId: string; quantity: number; notes?: string }) =>
    api.post<ApiResponse<Cart>>(`/cart/${cartId}/items`, {
      item_id: data.itemId,
      quantity: data.quantity,
      notes: data.notes
    }).then(r => r.data.data),
  
  updateItem: (cartId: string, data: { cartItemId: string; quantity: number }) =>
    api.put<ApiResponse<Cart>>(`/cart/${cartId}/items`, {
      cart_item_id: data.cartItemId,
      quantity: data.quantity
    }).then(r => r.data.data),
  
  removeItem: (cartId: string, cartItemId: string) =>
    api.delete<ApiResponse<Cart>>(`/cart/${cartId}/items/${cartItemId}`).then(r => r.data.data),
  
  clearCart: (cartId: string) =>
    api.delete(`/cart/${cartId}`),

  submitOrder: (cartId: string, data: { userId: string; customerName?: string; customerPhone?: string; resourceId?: string }) =>
    api.post<ApiResponse<Cart>>(`/cart/${cartId}/submit`, {
      user_id: data.userId,
      customer_name: data.customerName,
      customer_phone: data.customerPhone,
      resource_id: data.resourceId
    }).then(r => r.data.data),

  approveOrder: (cartId: string, estimatedReadyTime?: number) =>
    api.post<ApiResponse<Cart>>(`/cart/${cartId}/approve`, null, { 
      params: estimatedReadyTime ? { estimated_ready_time: estimatedReadyTime } : undefined 
    }).then(r => r.data.data),

  rejectOrder: (cartId: string, reason?: string) =>
    api.post<ApiResponse<Cart>>(`/cart/${cartId}/reject`, null, { 
      params: reason ? { reason } : undefined 
    }).then(r => r.data.data),

  confirmOrder: (cartId: string, data?: { customerName?: string; customerPhone?: string; resourceId?: string }) =>
    api.post<ApiResponse<Cart>>(`/cart/${cartId}/confirm`, {
      customer_name: data?.customerName,
      customer_phone: data?.customerPhone,
      resource_id: data?.resourceId
    }).then(r => r.data.data),

  updateStatus: (cartId: string, status: CartStatus) =>
    api.patch<ApiResponse<Cart>>(`/cart/${cartId}/status`, { status }).then(r => r.data.data),

  updateItemStatus: (cartItemId: string, status: CartItemStatus, preparedBy?: string) =>
    api.patch<ApiResponse<Cart>>(`/cart/items/${cartItemId}/status`, { 
      status, 
      prepared_by: preparedBy 
    }).then(r => r.data.data),

  getPendingOrders: (businessId: string) =>
    api.get<ApiResponse<Cart[]>>(`/cart/business/${businessId}/pending`).then(r => r.data.data),

  getOrdersPendingApproval: (businessId: string) =>
    api.get<ApiResponse<Cart[]>>(`/cart/business/${businessId}/pending-approval`).then(r => r.data.data),

  getOrdersByStatus: (businessId: string, status: CartStatus) =>
    api.get<ApiResponse<Cart[]>>(`/cart/business/${businessId}/status/${status}`).then(r => r.data.data),
}

export const billApi = {
  createBill: (data: { cartId: string; taxPercent?: number; discountAmount?: number; serviceCharge?: number }) =>
    api.post<ApiResponse<Bill>>('/bills', {
      cart_id: data.cartId,
      tax_percent: data.taxPercent,
      discount_amount: data.discountAmount,
      service_charge: data.serviceCharge
    }).then(r => r.data.data),

  getBill: (billId: string) =>
    api.get<ApiResponse<Bill>>(`/bills/${billId}`).then(r => r.data.data),

  getBillByCart: (cartId: string) =>
    api.get<ApiResponse<Bill | null>>(`/bills/cart/${cartId}`).then(r => r.data.data),

  processPayment: (billId: string, data: { amount: number; paymentMode: PaymentMethod; paymentRef?: string }) =>
    api.post<ApiResponse<Bill>>(`/bills/${billId}/pay`, {
      amount: data.amount,
      payment_mode: data.paymentMode,
      payment_ref: data.paymentRef
    }).then(r => r.data.data),

  processSplitPayment: (billId: string, data: { billItemIds: string[]; paidByUserId: string; amount: number; paymentMode: PaymentMethod }) =>
    api.post<ApiResponse<Bill>>(`/bills/${billId}/split-pay`, {
      bill_item_ids: data.billItemIds,
      paid_by_user_id: data.paidByUserId,
      amount: data.amount,
      payment_mode: data.paymentMode
    }).then(r => r.data.data),

  getBillsByBusiness: (businessId: string, limit: number = 50) =>
    api.get<ApiResponse<Bill[]>>(`/bills/business/${businessId}`, { params: { limit } }).then(r => r.data.data),
}

export const assistantApi = {
  createSession: (data: { assistant_type: string; device_id?: string }) =>
    api.post<ApiResponse<{ session_id: string }>>('/assistant/sessions', data).then(r => r.data.data),
  
  sendText: (data: { session_id: string; text: string; device_id: string; business_id?: string }) =>
    api.post<ApiResponse<{ response: string; action?: string }>>('/assistant/text', data).then(r => r.data.data),
  
  endSession: (sessionId: string) =>
    api.post(`/assistant/sessions/${sessionId}/end`),
}

export const businessApi = {
  getAll: () =>
    api.get<ApiResponse<Business[]>>('/businesses').then(r => r.data.data),

  getById: (businessId: string) =>
    api.get<ApiResponse<Business>>(`/businesses/${businessId}`).then(r => r.data.data),

  getResources: (businessId: string) =>
    api.get<ApiResponse<Resource[]>>(`/businesses/${businessId}/resources`).then(r => r.data.data),

  getAvailableResources: (businessId: string) =>
    api.get<ApiResponse<Resource[]>>(`/businesses/${businessId}/resources/available`).then(r => r.data.data),

  occupyResource: (resourceId: string) =>
    api.post<ApiResponse<Resource>>(`/businesses/resources/${resourceId}/occupy`).then(r => r.data.data),

  freeResource: (resourceId: string) =>
    api.post<ApiResponse<Resource>>(`/businesses/resources/${resourceId}/free`).then(r => r.data.data),

  updateResourceStatus: (resourceId: string, status: string) =>
    api.patch<ApiResponse<Resource>>(`/businesses/resources/${resourceId}/status`, { status }).then(r => r.data.data),
}

export interface AuthUser {
  id: string
  name: string
  email: string
  phone: string | null
  isActive: boolean
  createdAt: string
}

export interface TeamMembership {
  id: string
  businessId: string
  userId: string
  role: 'admin' | 'staff'
  status: string
  isActive: boolean
  createdAt: string
}

export interface AuthResponse {
  user: AuthUser
  token: string
  memberships?: TeamMembership[]
}

export const authApi = {
  signup: (data: { name: string; email: string; password: string; phone?: string }) =>
    api.post<ApiResponse<AuthResponse>>('/auth/signup', data).then(r => r.data.data),

  signin: (data: { email: string; password: string }) =>
    api.post<ApiResponse<AuthResponse>>('/auth/signin', data).then(r => r.data.data),

  getMe: () =>
    api.get<ApiResponse<{ user: AuthUser; memberships: TeamMembership[] }>>('/auth/me').then(r => r.data.data),

  assignRole: (data: { business_id: string; user_id: string; role: 'admin' | 'staff' }) =>
    api.post<ApiResponse<TeamMembership>>('/auth/assign-role', data).then(r => r.data.data),

  removeRole: (businessId: string, userId: string) =>
    api.delete(`/auth/remove-role/${businessId}/${userId}`),

  getBusinessMembers: (businessId: string) =>
    api.get<ApiResponse<(TeamMembership & { user?: AuthUser })[]>>(`/auth/business/${businessId}/members`).then(r => r.data.data),
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
