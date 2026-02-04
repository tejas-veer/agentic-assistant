import { useEffect, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Monitor, Settings, ChefHat, ArrowLeft, Loader2, AlertCircle, Mic, Phone, User, LogOut } from 'lucide-react'
import { businessApi } from '../lib/api'
import type { Business } from '../lib/types'
import { useAuthStore } from '../lib/store'

export default function InterfaceSelectionPage() {
  const { businessId } = useParams<{ businessId: string }>()
  const navigate = useNavigate()
  const { user, isAuthenticated, isAdminOf, logout } = useAuthStore()
  const [business, setBusiness] = useState<Business | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isAdmin = businessId ? isAdminOf(businessId) : false

  useEffect(() => {
    if (businessId) {
      loadBusiness(businessId)
    }
  }, [businessId])

  const loadBusiness = async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await businessApi.getById(id)
      setBusiness(data)
    } catch (err) {
      console.error('Failed to load business:', err)
      setError('Business not found')
    } finally {
      setLoading(false)
    }
  }

  const handleAdminClick = (e: React.MouseEvent) => {
    if (!isAuthenticated) {
      e.preventDefault()
      navigate(`/login?business=${businessId}&redirect=/admin?business=${businessId}`)
    }
  }

  const handleKitchenClick = (e: React.MouseEvent) => {
    if (!isAuthenticated) {
      e.preventDefault()
      navigate(`/login?business=${businessId}&redirect=/kitchen?business=${businessId}`)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-brand-400 animate-spin mx-auto mb-4" />
          <p className="text-white/60">Loading...</p>
        </div>
      </div>
    )
  }

  if (error || !business) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center px-6">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="font-display text-2xl font-semibold text-white mb-2">Business Not Found</h2>
          <p className="text-white/60 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white rounded-xl font-medium transition-colors"
          >
            Back to Selection
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-950 relative overflow-hidden">
      <div 
        className="absolute inset-0 opacity-60"
        style={{ background: 'var(--gradient-mesh)' }}
      />
      
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
        <div className="absolute top-6 left-6 right-6 flex justify-between items-center">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Change Business</span>
          </button>

          {isAuthenticated && user ? (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-white/60">
                <User className="w-4 h-4" />
                <span className="text-sm">{user.name}</span>
                {isAdmin && (
                  <span className="px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-400 rounded-full">Admin</span>
                )}
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-1 text-white/40 hover:text-white/60 text-sm transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          ) : (
            <Link
              to={`/login?business=${businessId}`}
              className="flex items-center gap-2 text-brand-400 hover:text-brand-300 transition-colors"
            >
              <User className="w-5 h-5" />
              <span>Sign In</span>
            </Link>
          )}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="font-display text-5xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent">
            {business.name}
          </h1>
          <p className="text-lg md:text-xl text-white/60">
            Select an interface to continue
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl w-full">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Link to={`/business/${businessId}/resources`} className="block group">
              <div className="glass-card p-8 hover:bg-white/10 transition-all duration-300 group-hover:scale-[1.02] group-hover:border-brand-400/30 h-full">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-lg">
                    <Monitor className="w-7 h-7 text-white" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold">Customer Kiosk</h2>
                </div>
                <p className="text-white/60 mb-6">
                  Select your table and start ordering with our touch interface
                </p>
                <div className="flex items-center gap-2 text-brand-400 font-medium">
                  <span>Select Table</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Link 
              to={isAuthenticated ? `/admin?business=${businessId}` : '#'} 
              onClick={handleAdminClick}
              className="block group"
            >
              <div className="glass-card p-8 hover:bg-white/10 transition-all duration-300 group-hover:scale-[1.02] group-hover:border-emerald-400/30 h-full relative">
                {!isAuthenticated && (
                  <div className="absolute top-4 right-4 px-2 py-1 bg-amber-500/20 text-amber-400 text-xs rounded-full">
                    Login Required
                  </div>
                )}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg">
                    <Settings className="w-7 h-7 text-white" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold">Admin Panel</h2>
                </div>
                <p className="text-white/60 mb-6">
                  Manage orders, view analytics, and control menu items in real-time
                </p>
                <div className="flex items-center gap-2 text-emerald-400 font-medium">
                  <span>{isAuthenticated ? 'Open Dashboard' : 'Sign In to Access'}</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Link 
              to={isAuthenticated ? `/kitchen?business=${businessId}` : '#'} 
              onClick={handleKitchenClick}
              className="block group"
            >
              <div className="glass-card p-8 hover:bg-white/10 transition-all duration-300 group-hover:scale-[1.02] group-hover:border-amber-400/30 h-full relative">
                {!isAuthenticated && (
                  <div className="absolute top-4 right-4 px-2 py-1 bg-amber-500/20 text-amber-400 text-xs rounded-full">
                    Login Required
                  </div>
                )}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg">
                    <ChefHat className="w-7 h-7 text-white" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold">Kitchen Display</h2>
                </div>
                <p className="text-white/60 mb-6">
                  Real-time order queue for kitchen staff with item preparation tracking
                </p>
                <div className="flex items-center gap-2 text-amber-400 font-medium">
                  <span>{isAuthenticated ? 'Open Kitchen' : 'Sign In to Access'}</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            </Link>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-12 flex flex-wrap justify-center gap-8 text-white/40"
        >
          <div className="flex items-center gap-2">
            <Mic className="w-5 h-5" />
            <span>Voice Assistant</span>
          </div>
          <div className="flex items-center gap-2">
            <Phone className="w-5 h-5" />
            <span>Call Agent Ready</span>
          </div>
          <div className="flex items-center gap-2">
            <Monitor className="w-5 h-5" />
            <span>Multi-device Support</span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
