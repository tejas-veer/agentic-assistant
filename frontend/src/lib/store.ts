import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Cart, Order } from './api'

interface KioskState {
  sessionId: string
  deviceId: string
  cart: Cart | null
  currentOrder: Order | null
  assistantSessionId: string | null
  isVoiceActive: boolean
  setSessionId: (id: string) => void
  setCart: (cart: Cart | null) => void
  setCurrentOrder: (order: Order | null) => void
  setAssistantSession: (id: string | null) => void
  setVoiceActive: (active: boolean) => void
  reset: () => void
}

export const useKioskStore = create<KioskState>()(
  persist(
    (set) => ({
      sessionId: `session_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      deviceId: `kiosk_${Date.now()}`,
      cart: null,
      currentOrder: null,
      assistantSessionId: null,
      isVoiceActive: false,
      setSessionId: (id) => set({ sessionId: id }),
      setCart: (cart) => set({ cart }),
      setCurrentOrder: (order) => set({ currentOrder: order }),
      setAssistantSession: (id) => set({ assistantSessionId: id }),
      setVoiceActive: (active) => set({ isVoiceActive: active }),
      reset: () => set({
        sessionId: `session_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        cart: null,
        currentOrder: null,
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
  pendingOrders: Order[]
  selectedOrder: Order | null
  setPendingOrders: (orders: Order[]) => void
  setSelectedOrder: (order: Order | null) => void
  updateOrder: (order: Order) => void
}

export const useAdminStore = create<AdminState>((set) => ({
  pendingOrders: [],
  selectedOrder: null,
  setPendingOrders: (orders) => set({ pendingOrders: orders }),
  setSelectedOrder: (order) => set({ selectedOrder: order }),
  updateOrder: (order) => set((state) => ({
    pendingOrders: state.pendingOrders.map((o) => 
      o.id === order.id ? order : o
    ),
    selectedOrder: state.selectedOrder?.id === order.id ? order : state.selectedOrder,
  })),
}))

