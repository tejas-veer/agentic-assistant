import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Minus, Plus, Trash2, ShoppingBag } from 'lucide-react'
import { useKioskStore } from '@/lib/store'
import { cartApi, orderApi } from '@/lib/api'
import { formatPrice } from '@/lib/utils'

export default function CartPage() {
  const navigate = useNavigate()
  const { sessionId, cart, setCart, setCurrentOrder, reset } = useKioskStore()
  const [isPlacingOrder, setIsPlacingOrder] = useState(false)
  const [tableNumber, setTableNumber] = useState('')
  const [customerName, setCustomerName] = useState('')

  const handleUpdateQuantity = async (menuItemId: string, quantity: number) => {
    try {
      const updatedCart = await cartApi.updateItem(sessionId, {
        menu_item_id: menuItemId,
        quantity,
      })
      setCart(updatedCart)
    } catch (error) {
      console.error('Failed to update quantity:', error)
    }
  }

  const handleRemoveItem = async (menuItemId: string) => {
    try {
      const updatedCart = await cartApi.removeItem(sessionId, menuItemId)
      setCart(updatedCart)
    } catch (error) {
      console.error('Failed to remove item:', error)
    }
  }

  const handlePlaceOrder = async () => {
    if (!cart || cart.items.length === 0) return

    setIsPlacingOrder(true)
    try {
      const order = await orderApi.createOrder({
        session_id: sessionId,
        table_number: tableNumber || undefined,
        customer_name: customerName || undefined,
      })
      setCurrentOrder(order)
      reset()
      navigate(`/kiosk/order/${order.order_number}`)
    } catch (error) {
      console.error('Failed to place order:', error)
    } finally {
      setIsPlacingOrder(false)
    }
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-12"
        >
          <ShoppingBag className="w-20 h-20 mx-auto mb-6 text-white/30" />
          <h2 className="font-display text-2xl font-semibold mb-4">Your cart is empty</h2>
          <p className="text-white/60 mb-8">Add some delicious items from our menu!</p>
          <Link to="/kiosk" className="btn-primary inline-flex items-center gap-2">
            <ArrowLeft className="w-5 h-5" />
            Browse Menu
          </Link>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4 mb-8"
      >
        <Link to="/kiosk" className="p-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <div>
          <h1 className="font-display text-3xl font-bold">Your Order</h1>
          <p className="text-white/60">{cart.items.length} items</p>
        </div>
      </motion.div>

      <div className="grid md:grid-cols-5 gap-8">
        <div className="md:col-span-3 space-y-4">
          <AnimatePresence mode="popLayout">
            {cart.items.map((item, i) => (
              <motion.div
                key={item.menu_item_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20, height: 0 }}
                transition={{ delay: i * 0.05 }}
                className="glass-card p-4 flex items-center gap-4"
              >
                <div className="w-20 h-20 rounded-xl bg-surface-900 flex items-center justify-center text-3xl flex-shrink-0">
                  🍽️
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">{item.menu_item_name}</h3>
                  <p className="text-brand-400 font-medium">{formatPrice(item.unit_price)}</p>
                </div>

                <div className="flex items-center gap-2">
                  <motion.button
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleUpdateQuantity(item.menu_item_id, item.quantity - 1)}
                    className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                  >
                    <Minus className="w-4 h-4" />
                  </motion.button>
                  <span className="w-8 text-center font-semibold">{item.quantity}</span>
                  <motion.button
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleUpdateQuantity(item.menu_item_id, item.quantity + 1)}
                    className="w-8 h-8 rounded-lg bg-brand-500 hover:bg-brand-600 flex items-center justify-center transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </motion.button>
                </div>

                <div className="text-right min-w-[80px]">
                  <p className="font-bold">{formatPrice(item.total_price)}</p>
                </div>

                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={() => handleRemoveItem(item.menu_item_id)}
                  className="p-2 rounded-lg text-red-400 hover:bg-red-500/20 transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </motion.button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="md:col-span-2"
        >
          <div className="glass-card p-6 sticky top-24">
            <h2 className="font-display text-xl font-semibold mb-6">Order Summary</h2>

            <div className="space-y-4 mb-6">
              <input
                type="text"
                placeholder="Table Number (optional)"
                value={tableNumber}
                onChange={(e) => setTableNumber(e.target.value)}
                className="w-full input-field"
              />
              <input
                type="text"
                placeholder="Your Name (optional)"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full input-field"
              />
            </div>

            <div className="space-y-3 mb-6 text-sm">
              <div className="flex justify-between">
                <span className="text-white/60">Subtotal</span>
                <span>{formatPrice(cart.subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/60">Tax</span>
                <span>{formatPrice(cart.tax)}</span>
              </div>
              <div className="h-px bg-white/10" />
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span className="text-brand-400">{formatPrice(cart.total)}</span>
              </div>
            </div>

            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={handlePlaceOrder}
              disabled={isPlacingOrder}
              className="w-full btn-primary py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPlacingOrder ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Placing Order...
                </span>
              ) : (
                `Place Order • ${formatPrice(cart.total)}`
              )}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

