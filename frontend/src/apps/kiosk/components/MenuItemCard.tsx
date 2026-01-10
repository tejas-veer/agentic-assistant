import { useState } from 'react'
import { motion } from 'framer-motion'
import { Plus, Minus, Check } from 'lucide-react'
import type { MenuItem } from '@/lib/api'
import { formatPrice } from '@/lib/utils'
import { useKioskStore } from '@/lib/store'
import { cartApi } from '@/lib/api'

interface MenuItemCardProps {
  item: MenuItem
  delay?: number
}

export default function MenuItemCard({ item, delay = 0 }: MenuItemCardProps) {
  const { sessionId, deviceId, cart, setCart } = useKioskStore()
  const [isAdding, setIsAdding] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const cartItem = cart?.items.find(i => i.menu_item_id === item.id)
  const quantity = cartItem?.quantity || 0

  const handleAdd = async () => {
    setIsAdding(true)
    try {
      const updatedCart = await cartApi.addItem(sessionId, deviceId, {
        menu_item_id: item.id,
        quantity: 1,
      })
      setCart(updatedCart)
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 1500)
    } catch (error) {
      console.error('Failed to add item:', error)
    } finally {
      setIsAdding(false)
    }
  }

  const handleUpdateQuantity = async (newQuantity: number) => {
    try {
      const updatedCart = await cartApi.updateItem(sessionId, {
        menu_item_id: item.id,
        quantity: newQuantity,
      })
      setCart(updatedCart)
    } catch (error) {
      console.error('Failed to update quantity:', error)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="glass-card overflow-hidden group hover:bg-surface-700/90 transition-all duration-300"
    >
      <div className="aspect-[4/3] relative overflow-hidden bg-surface-900">
        {item.image_url ? (
          <img 
            src={item.image_url} 
            alt={item.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-6xl">
            🍽️
          </div>
        )}
        
        {!item.is_available && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <span className="text-white font-semibold px-4 py-2 bg-red-500/80 rounded-lg">
              Sold Out
            </span>
          </div>
        )}

        {showSuccess && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="absolute inset-0 bg-emerald-500/80 flex items-center justify-center"
          >
            <Check className="w-16 h-16 text-white" />
          </motion.div>
        )}
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-lg line-clamp-1">{item.name}</h3>
          <span className="text-brand-400 font-bold whitespace-nowrap">
            {formatPrice(item.price)}
          </span>
        </div>

        {item.description && (
          <p className="text-white/50 text-sm line-clamp-2 mb-4">
            {item.description}
          </p>
        )}

        <div className="flex items-center gap-2">
          {quantity > 0 ? (
            <div className="flex items-center gap-2 flex-1">
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => handleUpdateQuantity(quantity - 1)}
                className="w-10 h-10 rounded-xl bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
              >
                <Minus className="w-4 h-4" />
              </motion.button>
              <span className="flex-1 text-center font-semibold text-lg">{quantity}</span>
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => handleUpdateQuantity(quantity + 1)}
                className="w-10 h-10 rounded-xl bg-brand-500 hover:bg-brand-600 flex items-center justify-center transition-colors"
              >
                <Plus className="w-4 h-4" />
              </motion.button>
            </div>
          ) : (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={handleAdd}
              disabled={!item.is_available || isAdding}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add to Cart</span>
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

