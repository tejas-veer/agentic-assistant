import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { ClipboardList, Clock, CheckCircle, DollarSign, ArrowRight } from 'lucide-react'
import { orderApi } from '@/lib/api'
import { useAdminStore } from '@/lib/store'
import { formatPrice, formatTime, getStatusColor } from '@/lib/utils'

export default function DashboardPage() {
  const { setPendingOrders } = useAdminStore()

  const { data: orders, refetch } = useQuery({
    queryKey: ['pending-orders'],
    queryFn: orderApi.getPendingOrders,
    refetchInterval: 5000,
  })

  useEffect(() => {
    if (orders) {
      setPendingOrders(orders)
    }
  }, [orders, setPendingOrders])

  const stats = {
    pending: orders?.filter(o => o.status === 'pending').length || 0,
    preparing: orders?.filter(o => o.status === 'preparing').length || 0,
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: 'Pending Orders', value: stats.pending, icon: Clock, color: 'amber' },
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
                  <span className="font-semibold">{order.order_number}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                    {order.status}
                  </span>
                </div>
                <p className="text-white/60 text-sm">
                  {order.items.length} items • {order.customer_name || 'Guest'}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold">{formatPrice(order.total)}</p>
                <p className="text-white/40 text-sm">{formatTime(order.created_at)}</p>
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

