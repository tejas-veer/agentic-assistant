import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ClipboardList, Clock, CheckCircle, DollarSign, ArrowRight, AlertCircle, Check, X } from 'lucide-react'
import { cartApi } from '@/lib/api'
import { useAdminStore } from '@/lib/store'
import { formatPrice, formatTime, getStatusColor } from '@/lib/utils'

export default function DashboardPage() {
  const { businessId, setPendingOrders } = useAdminStore()
  const queryClient = useQueryClient()
  const [approving, setApproving] = useState<string | null>(null)

  const { data: orders } = useQuery({
    queryKey: ['pending-orders', businessId],
    queryFn: () => cartApi.getPendingOrders(businessId),
    refetchInterval: 5000,
  })

  const { data: pendingApproval } = useQuery({
    queryKey: ['pending-approval', businessId],
    queryFn: () => cartApi.getOrdersPendingApproval(businessId),
    refetchInterval: 5000,
  })

  useEffect(() => {
    if (orders) {
      setPendingOrders(orders)
    }
  }, [orders, setPendingOrders])

  const handleApprove = async (orderId: string) => {
    setApproving(orderId)
    try {
      await cartApi.approveOrder(orderId)
      queryClient.invalidateQueries({ queryKey: ['pending-approval'] })
      queryClient.invalidateQueries({ queryKey: ['pending-orders'] })
    } catch (error) {
      console.error('Failed to approve order:', error)
    } finally {
      setApproving(null)
    }
  }

  const handleReject = async (orderId: string) => {
    setApproving(orderId)
    try {
      await cartApi.rejectOrder(orderId)
      queryClient.invalidateQueries({ queryKey: ['pending-approval'] })
    } catch (error) {
      console.error('Failed to reject order:', error)
    } finally {
      setApproving(null)
    }
  }

  const stats = {
    awaitingApproval: pendingApproval?.length || 0,
    pending: orders?.filter(o => o.status === 'confirmed').length || 0,
    preparing: orders?.filter(o => o.status === 'in_progress').length || 0,
    ready: orders?.filter(o => o.status === 'ready').length || 0,
    total: orders?.reduce((sum, o) => sum + o.total, 0) || 0,
  }

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-display text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-white/60">Real-time order management</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {[
          { label: 'Awaiting Approval', value: stats.awaitingApproval, icon: AlertCircle, color: 'red' },
          { label: 'Confirmed', value: stats.pending, icon: Clock, color: 'amber' },
          { label: 'Preparing', value: stats.preparing, icon: ClipboardList, color: 'purple' },
          { label: 'Ready', value: stats.ready, icon: CheckCircle, color: 'emerald' },
          { label: 'Today\'s Revenue', value: formatPrice(stats.total), icon: DollarSign, color: 'blue' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl bg-${stat.color}-500/20 flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
              </div>
            </div>
            <p className="text-white/60 text-sm mb-1">{stat.label}</p>
            <p className="font-display text-3xl font-bold">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Orders Awaiting Approval */}
      {pendingApproval && pendingApproval.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card mb-8 border-red-500/30"
        >
          <div className="p-6 border-b border-white/10 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <h2 className="font-display text-xl font-semibold">Orders Awaiting Approval</h2>
            <span className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full text-sm font-medium">
              {pendingApproval.length}
            </span>
          </div>

          <div className="divide-y divide-white/10">
            {pendingApproval.map((order, i) => (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.05 }}
                className="p-4 flex items-center gap-4"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-semibold">{order.id.slice(0, 8).toUpperCase()}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                      Pending Approval
                    </span>
                  </div>
                  <p className="text-white/60 text-sm">
                    {order.items?.length || 0} items • {order.customerName || 'Guest'} • {formatPrice(order.total)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleReject(order.id)}
                    disabled={approving === order.id}
                    className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 transition-colors disabled:opacity-50"
                    title="Reject"
                  >
                    <X className="w-5 h-5" />
                  </motion.button>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleApprove(order.id)}
                    disabled={approving === order.id}
                    className="p-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 transition-colors disabled:opacity-50"
                    title="Approve"
                  >
                    <Check className="w-5 h-5" />
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card"
      >
        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          <h2 className="font-display text-xl font-semibold">Recent Orders</h2>
          <Link 
            to="/admin/orders" 
            className="text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors"
          >
            View All <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="divide-y divide-white/10">
          {orders?.slice(0, 5).map((order, i) => (
            <motion.div
              key={order.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.05 }}
              className="p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-semibold">{order.id.slice(0, 8).toUpperCase()}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                    {order.status.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-white/60 text-sm">
                  {order.items?.length || 0} items • {order.customerName || 'Guest'}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold">{formatPrice(order.total)}</p>
                <p className="text-white/40 text-sm">{formatTime(order.createdAt)}</p>
              </div>
            </motion.div>
          ))}

          {(!orders || orders.length === 0) && (
            <div className="p-12 text-center text-white/40">
              No pending orders
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
