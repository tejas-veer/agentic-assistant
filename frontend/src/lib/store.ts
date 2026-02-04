import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Cart, Bill, Category } from './types'

interface KioskState {
  sessionId: string
  deviceId: string
  businessId: string
  cartId: string | null
  cart: Cart | null
  currentBill: Bill | null
  assistantSessionId: string | null
  isVoiceActive: boolean
  categories: Category[]
  setSessionId: (id: string) => void
  setBusinessId: (id: string) => void
  setCartId: (id: string | null) => void
  setCart: (cart: Cart | null) => void
  setCurrentBill: (bill: Bill | null) => void
  setAssistantSession: (id: string | null) => void
  setVoiceActive: (active: boolean) => void
  setCategories: (categories: Category[]) => void
  reset: () => void
}

export const useKioskStore = create<KioskState>()(
  persist(
    (set) => ({
      sessionId: `session_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      deviceId: `kiosk_${Date.now()}`,
      businessId: '1',
      cartId: null,
      cart: null,
      currentBill: null,
      assistantSessionId: null,
      isVoiceActive: false,
      categories: [],
      setSessionId: (id) => set({ sessionId: id }),
      setBusinessId: (id) => set({ businessId: id }),
      setCartId: (id) => set({ cartId: id }),
      setCart: (cart) => set({ cart }),
      setCurrentBill: (bill) => set({ currentBill: bill }),
      setAssistantSession: (id) => set({ assistantSessionId: id }),
      setVoiceActive: (active) => set({ isVoiceActive: active }),
      setCategories: (categories) => set({ categories }),
      reset: () => set({
        sessionId: `session_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        cartId: null,
        cart: null,
        currentBill: null,
        assistantSessionId: null,
        isVoiceActive: false,
      }),
    }),
    {
      name: 'kiosk-storage',
    }
  )
)

interface AdminState {
  businessId: string
  pendingOrders: Cart[]
  selectedOrder: Cart | null
  setBusinessId: (id: string) => void
  setPendingOrders: (orders: Cart[]) => void
  setSelectedOrder: (order: Cart | null) => void
  updateOrder: (order: Cart) => void
}

export const useAdminStore = create<AdminState>((set) => ({
  businessId: '1',
  pendingOrders: [],
  selectedOrder: null,
  setBusinessId: (id) => set({ businessId: id }),
  setPendingOrders: (orders) => set({ pendingOrders: orders }),
  setSelectedOrder: (order) => set({ selectedOrder: order }),
  updateOrder: (order) => set((state) => ({
    pendingOrders: state.pendingOrders.map((o) => 
      o.id === order.id ? order : o
    ),
    selectedOrder: state.selectedOrder?.id === order.id ? order : state.selectedOrder,
  })),
}))
