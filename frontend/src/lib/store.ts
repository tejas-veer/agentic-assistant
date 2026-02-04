import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Cart, Bill, Category } from './types'
import type { AuthUser, TeamMembership } from './api'

export const DEFAULT_BUSINESS_ID = 'biz00001-0000-0000-0000-000000000001'

interface AuthState {
  user: AuthUser | null
  token: string | null
  memberships: TeamMembership[]
  isAuthenticated: boolean
  setAuth: (user: AuthUser, token: string, memberships: TeamMembership[]) => void
  logout: () => void
  getMembershipForBusiness: (businessId: string) => TeamMembership | undefined
  isAdminOf: (businessId: string) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      memberships: [],
      isAuthenticated: false,
      setAuth: (user, token, memberships) => {
        localStorage.setItem('auth_token', token)
        set({ user, token, memberships, isAuthenticated: true })
      },
      logout: () => {
        localStorage.removeItem('auth_token')
        set({ user: null, token: null, memberships: [], isAuthenticated: false })
      },
      getMembershipForBusiness: (businessId: string) => {
        return get().memberships.find(m => m.businessId === businessId && m.isActive)
      },
      isAdminOf: (businessId: string) => {
        const membership = get().getMembershipForBusiness(businessId)
        return membership?.role === 'admin'
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)

interface KioskState {
  sessionId: string
  deviceId: string
  businessId: string
  resourceId: string | null
  resourceName: string | null
  cartId: string | null
  cart: Cart | null
  currentBill: Bill | null
  assistantSessionId: string | null
  isVoiceActive: boolean
  categories: Category[]
  setSessionId: (id: string) => void
  setBusinessId: (id: string) => void
  setResource: (id: string | null, name: string | null) => void
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
      businessId: DEFAULT_BUSINESS_ID,
      resourceId: null,
      resourceName: null,
      cartId: null,
      cart: null,
      currentBill: null,
      assistantSessionId: null,
      isVoiceActive: false,
      categories: [],
      setSessionId: (id) => set({ sessionId: id }),
      setBusinessId: (id) => set({ businessId: id }),
      setResource: (id, name) => set({ resourceId: id, resourceName: name }),
      setCartId: (id) => set({ cartId: id }),
      setCart: (cart) => set({ cart }),
      setCurrentBill: (bill) => set({ currentBill: bill }),
      setAssistantSession: (id) => set({ assistantSessionId: id }),
      setVoiceActive: (active) => set({ isVoiceActive: active }),
      setCategories: (categories) => set({ categories }),
      reset: () => set({
        sessionId: `session_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        resourceId: null,
        resourceName: null,
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
  businessId: DEFAULT_BUSINESS_ID,
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
