export const TAX_RATE = 0.08

export const MAX_CART_ITEMS = 50
export const MAX_ITEM_QUANTITY = 10

export const SESSION_TIMEOUT_MS = 60 * 60 * 1000

export const API_TIMEOUT_MS = 30000

export const ANIMATION_DURATION = {
  fast: 150,
  normal: 300,
  slow: 500,
} as const

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
} as const

export const CATEGORY_EMOJIS: Record<string, string> = {
  'Burgers': '🍔',
  'Pizzas': '🍕',
  'Sides': '🍟',
  'Drinks': '🥤',
  'Desserts': '🍰',
}

