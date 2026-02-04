import { useState } from 'react'
import { motion } from 'framer-motion'
import { Plus, Minus, Check } from 'lucide-react'
import type { MenuItem } from '@/lib/types'
import { formatPrice } from '@/lib/utils'
import { useKioskStore } from '@/lib/store'
import { cartApi } from '@/lib/api'

interface MenuItemCardProps {
  item: MenuItem
  delay?: number
}

export default function MenuItemCard({ item, delay = 0 }: MenuItemCardProps) {
  const { businessId, sessionId, deviceId, cartId, cart, setCartId, setCart } = useKioskStore()
  const [isAdding, setIsAdding] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const cartItem = cart?.items?.find(i => i.itemId === item.id)
  const quantity = cartItem?.quantity || 0

  const ensureCart = async (): Promise<string> => {
    if (cartId) return cartId
    
    const result = await cartApi.createCart({
      businessId,
      sessionId,
      deviceId,
    })
    setCartId(result.id)
    return result.id
  }

  const handleAdd = async () => {
    setIsAdding(true)
    try {
      const currentCartId = await ensureCart()
      const updatedCart = await cartApi.addItem(currentCartId, {
        itemId: item.id,
        quantity: 1,
      })
      setCart(updatedCart)
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 1500)
    } catch (error) {
      console.error('Failed to add item:', error)
      // If cart error (e.g., cart doesn't exist), clear and retry with new cart
      setCartId(null)
      setCart(null)
      try {
        const result = await cartApi.createCart({ businessId, sessionId, deviceId })
        setCartId(result.id)
        const updatedCart = await cartApi.addItem(result.id, { itemId: item.id, quantity: 1 })
        setCart(updatedCart)
        setShowSuccess(true)
        setTimeout(() => setShowSuccess(false), 1500)
      } catch (retryError) {
        console.error('Failed to create cart and add item:', retryError)
      }
    } finally {
      setIsAdding(false)
    }
  }

  const handleUpdateQuantity = async (newQuantity: number) => {
    if (!cartId || !cartItem) return
    try {
      if (newQuantity <= 0) {
        const updatedCart = await cartApi.removeItem(cartId, cartItem.id)
        setCart(updatedCart)
      } else {
        const updatedCart = await cartApi.updateItem(cartId, {
          cartItemId: cartItem.id,
          quantity: newQuantity,
        })
        setCart(updatedCart)
      }
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
        {item.imageUrl ? (
          <img 
            src={item.imageUrl} 
            alt={item.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-6xl">
            🍽️
          </div>
        )}
        
        {!item.available && (
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
              disabled={!item.available || isAdding}
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
