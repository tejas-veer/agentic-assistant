import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { menuApi, cartApi } from '@/lib/api'
import { useKioskStore } from '@/lib/store'
import MenuItemCard from '../components/MenuItemCard'

export default function MenuPage() {
  const { businessId, sessionId, cartId, setCartId, setCart, setCategories } = useKioskStore()
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const { data: menu, isLoading } = useQuery({
    queryKey: ['menu', businessId],
    queryFn: () => menuApi.getMenu(businessId),
  })

  useEffect(() => {
    if (menu && menu.length > 0) {
      setCategories(menu)
      if (!activeCategory) {
        setActiveCategory(menu[0].id)
      }
    }
  }, [menu, activeCategory, setCategories])

  useEffect(() => {
    const loadOrCreateCart = async () => {
      try {
        if (cartId) {
          const cart = await cartApi.getCart(cartId)
          if (cart) {
            setCart(cart)
            return
          } else {
            // Cart no longer exists (e.g., DB was re-seeded), clear it
            setCartId(null)
            setCart(null)
          }
        }
        
        const cartBySession = await cartApi.getCartBySession(sessionId)
        if (cartBySession) {
          setCartId(cartBySession.id)
          setCart(cartBySession)
        }
      } catch (error) {
        console.error('Failed to load cart:', error)
        // Clear invalid cart ID on error
        setCartId(null)
        setCart(null)
      }
    }
    loadOrCreateCart()
  }, [sessionId, cartId, setCart, setCartId])

  const filteredMenu = menu?.map(category => ({
    ...category,
    items: (category.items || []).filter(item =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => category.items.length > 0)

  const currentCategory = activeCategory 
    ? filteredMenu?.find(c => c.id === activeCategory)
    : filteredMenu?.[0]

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-display text-4xl md:text-5xl font-bold mb-4">
          What are you craving?
        </h1>
        <p className="text-white/60 text-lg">
          Browse our menu or use voice assistant to order
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 bg-surface-900/80 border border-white/10 rounded-xl px-4 h-14 focus-within:ring-2 focus-within:ring-brand-400/50 focus-within:border-brand-400/50 transition-all duration-200">
          <Search className="w-5 h-5 text-white/40 flex-shrink-0" />
          <input
            type="text"
            placeholder="Search menu items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 bg-transparent text-white text-lg placeholder:text-white/40 focus:outline-none"
          />
        </div>
      </motion.div>

      <div className="flex gap-3 overflow-x-auto pb-4 mb-8 scrollbar-hide">
        {filteredMenu?.map((category, i) => (
          <motion.button
            key={category.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            onClick={() => setActiveCategory(category.id)}
            className={`px-6 py-3 rounded-xl font-medium whitespace-nowrap transition-all ${
              activeCategory === category.id
                ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/30'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            {category.name}
          </motion.button>
        ))}
      </div>

      {currentCategory && (
        <div>
          <motion.h2
            key={currentCategory.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="font-display text-2xl font-semibold mb-6"
          >
            {currentCategory.name}
          </motion.h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {currentCategory.items.map((item, i) => (
              <MenuItemCard 
                key={item.id} 
                item={item} 
                delay={i * 0.05}
              />
            ))}
          </div>
        </div>
      )}

      {filteredMenu?.length === 0 && (
        <div className="text-center py-16">
          <p className="text-white/60 text-lg">No items found matching your search.</p>
        </div>
      )}
    </div>
  )
}
