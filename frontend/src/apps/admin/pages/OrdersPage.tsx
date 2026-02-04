import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, X, Clock, ChefHat, Package } from 'lucide-react'
import { cartApi } from '@/lib/api'
import type { Cart, CartStatus } from '@/lib/types'
import { useAdminStore } from '@/lib/store'
import { formatPrice, formatTime, getStatusColor } from '@/lib/utils'

export default function OrdersPage() {
  const queryClient = useQueryClient()
  const { businessId } = useAdminStore()
  const [selectedOrder, setSelectedOrder] = useState<Cart | null>(null)

  const { data: orders } = useQuery({
    queryKey: ['pending-orders', businessId],
    queryFn: () => cartApi.getPendingOrders(businessId),
    refetchInterval: 3000,
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ cartId, status }: { cartId: string; status: CartStatus }) =>
      cartApi.updateStatus(cartId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-orders'] })
    },
  })

  const handleStatusChange = (cartId: string, newStatus: CartStatus) => {
    updateStatusMutation.mutate({ cartId, status: newStatus })
    if (selectedOrder?.id === cartId) {
      setSelectedOrder({ ...selectedOrder, status: newStatus })
    }
  }

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-display text-3xl font-bold mb-2">Order Management</h1>
        <p className="text-white/60">Manage and track all incoming orders</p>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h2 className="font-semibold">Active Orders</h2>
              <span className="text-white/60 text-sm">{orders?.length || 0} orders</span>
            </div>

            <div className="divide-y divide-white/10 max-h-[calc(100vh-300px)] overflow-y-auto">
              <AnimatePresence mode="popLayout">
                {orders?.map((order) => (
                  <motion.div
                    key={order.id}
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    onClick={() => setSelectedOrder(order)}
                    className={`p-4 cursor-pointer hover:bg-white/5 transition-colors ${
                      selectedOrder?.id === order.id ? 'bg-white/5' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="font-display font-bold text-lg">{order.id.slice(0, 8).toUpperCase()}</span>
                        {order.resourceId && (
                          <span className="px-2 py-0.5 bg-white/10 rounded text-sm">
                            Resource
                          </span>
                        )}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(order.status)}`}>
                        {order.status.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <div className="text-white/60">
                        {order.items?.map(i => `${i.quantity}x ${i.itemName}`).join(', ') || 'No items'}
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-semibold">{formatPrice(order.total)}</span>
                        <span className="text-white/40">{formatTime(order.createdAt)}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {(!orders || orders.length === 0) && (
                <div className="p-12 text-center text-white/40">
                  <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No active orders</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div>
          <AnimatePresence mode="wait">
            {selectedOrder ? (
              <motion.div
                key={selectedOrder.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="glass-card sticky top-8"
              >
                <div className="p-4 border-b border-white/10">
                  <h3 className="font-display text-xl font-bold">{selectedOrder.id.slice(0, 8).toUpperCase()}</h3>
                  <p className="text-white/60 text-sm">{formatTime(selectedOrder.createdAt)}</p>
                </div>

                <div className="p-4 space-y-4">
                  {selectedOrder.customerName && (
                    <div>
                      <span className="text-white/40 text-sm">Customer</span>
                      <p className="font-medium">{selectedOrder.customerName}</p>
                    </div>
                  )}

                  {selectedOrder.customerPhone && (
                    <div>
                      <span className="text-white/40 text-sm">Phone</span>
                      <p className="font-medium">{selectedOrder.customerPhone}</p>
                    </div>
                  )}

                  <div>
                    <span className="text-white/40 text-sm block mb-2">Items</span>
                    <div className="space-y-2">
                      {selectedOrder.items?.map((item, i) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span>{item.quantity}x {item.itemName}</span>
                          <span>{formatPrice(item.totalPrice)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="h-px bg-white/10" />

                  <div className="flex justify-between font-bold">
                    <span>Total</span>
                    <span className="text-emerald-400">{formatPrice(selectedOrder.total)}</span>
                  </div>
                </div>

                <div className="p-4 border-t border-white/10 space-y-3">
                  <div className="flex gap-2">
                    {selectedOrder.status === 'confirmed' && (
                      <button
                        onClick={() => handleStatusChange(selectedOrder.id, 'in_progress')}
                        className="flex-1 py-2 px-4 bg-purple-500 hover:bg-purple-600 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
                      >
                        <ChefHat className="w-4 h-4" /> Start Preparing
                      </button>
                    )}

                    {selectedOrder.status === 'in_progress' && (
                      <button
                        onClick={() => handleStatusChange(selectedOrder.id, 'ready')}
                        className="flex-1 py-2 px-4 bg-emerald-500 hover:bg-emerald-600 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
                      >
                        <Check className="w-4 h-4" /> Mark Ready
                      </button>
                    )}

                    {selectedOrder.status === 'ready' && (
                      <button
                        onClick={() => handleStatusChange(selectedOrder.id, 'completed')}
                        className="flex-1 py-2 px-4 bg-blue-500 hover:bg-blue-600 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
                      >
                        <Package className="w-4 h-4" /> Complete
                      </button>
                    )}

                    {(selectedOrder.status === 'confirmed' || selectedOrder.status === 'in_progress') && (
                      <button
                        onClick={() => handleStatusChange(selectedOrder.id, 'cancelled')}
                        className="py-2 px-4 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass-card p-8 text-center text-white/40"
              >
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select an order to view details</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
