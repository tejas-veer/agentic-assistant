import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { CheckCircle, Clock, Home, RefreshCw, Hourglass, XCircle } from 'lucide-react'
import { cartApi } from '@/lib/api'
import { useKioskStore } from '@/lib/store'
import type { Cart } from '@/lib/types'
import { formatPrice, getStatusColor } from '@/lib/utils'

export default function OrderConfirmation() {
  const { orderNumber } = useParams<{ orderNumber: string }>()
  const { resourceName } = useKioskStore()
  const [order, setOrder] = useState<Cart | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadOrder()
    const interval = setInterval(loadOrder, 5000)
    return () => clearInterval(interval)
  }, [orderNumber])

  const loadOrder = async () => {
    if (!orderNumber) return
    try {
      const data = await cartApi.getCart(orderNumber)
      setOrder(data)
    } catch (error) {
      console.error('Failed to load order:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!order) {
    return (
      <div className="max-w-xl mx-auto px-6 py-16 text-center">
        <h2 className="font-display text-2xl font-semibold mb-4">Order not found</h2>
        <Link to="/kiosk" className="btn-primary inline-flex items-center gap-2">
          <Home className="w-5 h-5" />
          Back to Menu
        </Link>
      </div>
    )
  }

  const isPendingApproval = order.status === 'pending_approval'
  const isRejected = order.status === 'cancelled'
  const statusSteps = ['pending_approval', 'confirmed', 'in_progress', 'ready', 'completed']
  const currentStepIndex = statusSteps.indexOf(order.status)
  const displaySteps = ['Submitted', 'Approved', 'Preparing', 'Ready', 'Done']

  return (
    <div className="max-w-2xl mx-auto px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-8 text-center mb-8"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.2 }}
          className={`w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center ${
            isRejected 
              ? 'bg-red-500/20' 
              : isPendingApproval 
                ? 'bg-amber-500/20' 
                : 'bg-emerald-500/20'
          }`}
        >
          {isRejected ? (
            <XCircle className="w-12 h-12 text-red-400" />
          ) : isPendingApproval ? (
            <Hourglass className="w-12 h-12 text-amber-400 animate-pulse" />
          ) : (
            <CheckCircle className="w-12 h-12 text-emerald-400" />
          )}
        </motion.div>

        <h1 className="font-display text-3xl font-bold mb-2">
          {isRejected ? 'Order Rejected' : isPendingApproval ? 'Awaiting Approval' : 'Order Confirmed!'}
        </h1>
        <p className="text-white/60 text-lg mb-6">
          {isRejected 
            ? order.notes || 'Your order was not approved'
            : isPendingApproval 
              ? 'Your order is being reviewed by the restaurant'
              : 'Thank you for your order'
          }
        </p>

        <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/10 rounded-2xl mb-4">
          <span className="text-white/60">Order ID:</span>
          <span className="font-display text-xl font-bold text-brand-400">{order.id.slice(0, 8).toUpperCase()}</span>
        </div>

        {resourceName && (
          <div className="mb-4">
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-brand-500/20 text-brand-400 rounded-xl text-sm">
              🪑 {resourceName}
            </span>
          </div>
        )}

        {order.estimatedReadyTime && !isPendingApproval && !isRejected && (
          <div className="flex items-center justify-center gap-2 text-white/60">
            <Clock className="w-5 h-5" />
            <span>Estimated ready in {order.estimatedReadyTime} minutes</span>
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-card p-6 mb-8"
      >
        <h2 className="font-semibold mb-6">Order Status</h2>
        
        <div className="flex justify-between relative mb-2">
          <div className="absolute top-4 left-0 right-0 h-1 bg-white/10 rounded-full">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.max(0, (currentStepIndex / (statusSteps.length - 1)) * 100)}%` }}
              className="h-full bg-gradient-to-r from-brand-400 to-brand-600 rounded-full"
            />
          </div>
          
          {displaySteps.map((step, i) => (
            <div key={step} className="relative z-10 flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                i <= currentStepIndex 
                  ? 'bg-brand-500 text-white' 
                  : 'bg-white/10 text-white/40'
              }`}>
                {i < currentStepIndex ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <span className="text-sm font-medium">{i + 1}</span>
                )}
              </div>
              <span className={`mt-2 text-xs ${
                i <= currentStepIndex ? 'text-white' : 'text-white/40'
              }`}>
                {step}
              </span>
            </div>
          ))}
        </div>

        <div className="text-center mt-6">
          <span className={`inline-flex px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(order.status)}`}>
            {order.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </span>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6 mb-8"
      >
        <h2 className="font-semibold mb-4">Order Details</h2>
        
        <div className="space-y-3">
          {order.items?.map((item, i) => (
            <div key={i} className="flex justify-between text-sm">
              <span className="text-white/80">
                {item.quantity}x {item.itemName}
              </span>
              <span>{formatPrice(item.totalPrice)}</span>
            </div>
          ))}
          
          <div className="h-px bg-white/10 my-3" />
          
          <div className="flex justify-between text-sm">
            <span className="text-white/60">Subtotal</span>
            <span>{formatPrice(order.subtotal)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-white/60">Tax</span>
            <span>{formatPrice(order.tax)}</span>
          </div>
          <div className="flex justify-between font-bold text-lg">
            <span>Total</span>
            <span className="text-brand-400">{formatPrice(order.total)}</span>
          </div>
        </div>
      </motion.div>

      <div className="flex gap-4">
        <button
          onClick={loadOrder}
          className="flex-1 btn-secondary flex items-center justify-center gap-2"
        >
          <RefreshCw className="w-5 h-5" />
          Refresh Status
        </button>
        <Link to="/kiosk" className="flex-1 btn-primary flex items-center justify-center gap-2">
          <Home className="w-5 h-5" />
          New Order
        </Link>
      </div>
    </div>
  )
}
