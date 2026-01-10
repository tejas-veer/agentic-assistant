import axios from 'axios'

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

export interface MenuItem {
  id: string
  name: string
  description: string | null
  price: number
  image_url: string | null
  is_available: boolean
  preparation_time_mins: number
  tags: string[]
  customizations: unknown[]
}

export interface Category {
  id: string
  name: string
  description: string | null
  image_url: string | null
  items: MenuItem[]
}

export interface CartItem {
  menu_item_id: string
  menu_item_name: string
  quantity: number
  unit_price: number
  total_price: number
  customizations: string[]
  special_instructions: string | null
}

export interface Cart {
  id: string
  session_id: string
  device_id: string
  items: CartItem[]
  subtotal: number
  tax: number
  total: number
}

export interface Order {
  id: string
  order_number: string
  device_id: string
  table_number: string | null
  customer_name: string | null
  items: CartItem[]
  subtotal: number
  tax: number
  total: number
  status: string
  payment_status: string
  payment_method: string | null
  created_at: string
  estimated_ready_time: number | null
}

export const menuApi = {
  getMenu: () => api.get<{ success: boolean; data: Category[] }>('/menu').then(r => r.data.data),
  searchItems: (q: string) => api.get<{ success: boolean; data: MenuItem[] }>(`/menu/search?q=${q}`).then(r => r.data.data),
}

export const cartApi = {
  getCart: (sessionId: string) => 
    api.get<{ success: boolean; data: Cart | null }>(`/cart/${sessionId}`).then(r => r.data.data),
  
  addItem: (sessionId: string, deviceId: string, data: { menu_item_id: string; quantity: number }) =>
    api.post<{ success: boolean; data: Cart }>(`/cart/${sessionId}/items?device_id=${deviceId}`, data).then(r => r.data.data),
  
  updateItem: (sessionId: string, data: { menu_item_id: string; quantity: number }) =>
    api.put<{ success: boolean; data: Cart }>(`/cart/${sessionId}/items`, data).then(r => r.data.data),
  
  removeItem: (sessionId: string, menuItemId: string) =>
    api.delete<{ success: boolean; data: Cart }>(`/cart/${sessionId}/items/${menuItemId}`).then(r => r.data.data),
  
  clearCart: (sessionId: string) =>
    api.delete(`/cart/${sessionId}`),
}

export const orderApi = {
  createOrder: (data: { session_id: string; table_number?: string; customer_name?: string }) =>
    api.post<{ success: boolean; data: Order }>('/orders', data).then(r => r.data.data),
  
  getOrder: (orderId: string) =>
    api.get<{ success: boolean; data: Order }>(`/orders/${orderId}`).then(r => r.data.data),
  
  getOrderByNumber: (orderNumber: string) =>
    api.get<{ success: boolean; data: Order }>(`/orders/number/${orderNumber}`).then(r => r.data.data),
  
  getPendingOrders: () =>
    api.get<{ success: boolean; data: Order[] }>('/orders/pending').then(r => r.data.data),
  
  updateStatus: (orderId: string, status: string) =>
    api.patch<{ success: boolean; data: Order }>(`/orders/${orderId}/status`, { status }).then(r => r.data.data),
  
  confirmOrder: (orderId: string, estimatedTime?: number) =>
    api.post<{ success: boolean; data: Order }>(`/orders/${orderId}/confirm`, { estimated_ready_time: estimatedTime }).then(r => r.data.data),
  
  cancelOrder: (orderId: string, reason?: string) =>
    api.post<{ success: boolean; data: Order }>(`/orders/${orderId}/cancel?reason=${reason || ''}`).then(r => r.data.data),
}

export const assistantApi = {
  createSession: (data: { assistant_type: string; device_id?: string }) =>
    api.post<{ success: boolean; data: { session_id: string } }>('/assistant/sessions', data).then(r => r.data.data),
  
  sendText: (data: { session_id: string; text: string; device_id: string }) =>
    api.post<{ success: boolean; data: { response: string; action?: string } }>('/assistant/text', data).then(r => r.data.data),
  
  endSession: (sessionId: string) =>
    api.post(`/assistant/sessions/${sessionId}/end`),
}

export default api

