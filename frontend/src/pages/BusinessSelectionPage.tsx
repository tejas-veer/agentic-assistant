import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Store, Loader2, AlertCircle, Utensils, Building2, Stethoscope } from 'lucide-react'
import { businessApi } from '../lib/api'
import type { Business } from '../lib/types'
import { useKioskStore, useAdminStore } from '../lib/store'

const businessTypeIcons: Record<string, typeof Store> = {
  restaurant: Utensils,
  hotel: Building2,
  clinic: Stethoscope,
}

const businessTypeColors: Record<string, string> = {
  restaurant: 'from-orange-400 to-red-500',
  hotel: 'from-blue-400 to-indigo-500',
  clinic: 'from-emerald-400 to-teal-500',
}

export default function BusinessSelectionPage() {
  const navigate = useNavigate()
  const [businesses, setBusinesses] = useState<Business[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const setKioskBusinessId = useKioskStore((s) => s.setBusinessId)
  const setAdminBusinessId = useAdminStore((s) => s.setBusinessId)

  useEffect(() => {
    loadBusinesses()
  }, [])

  const loadBusinesses = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await businessApi.getAll()
      setBusinesses(data || [])
    } catch (err) {
      console.error('Failed to load businesses:', err)
      setError('Failed to load businesses. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectBusiness = (business: Business) => {
    setKioskBusinessId(business.id)
    setAdminBusinessId(business.id)
    navigate(`/business/${business.id}`)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-brand-400 animate-spin mx-auto mb-4" />
          <p className="text-white/60">Loading businesses...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center px-6">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="font-display text-2xl font-semibold text-white mb-2">Oops!</h2>
          <p className="text-white/60 mb-6">{error}</p>
          <button
            onClick={loadBusinesses}
            className="px-6 py-3 bg-brand-500 hover:bg-brand-600 text-white rounded-xl font-medium transition-colors"
          >
            Try Again
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
      
      <div className="relative z-10 min-h-screen flex flex-col items-center py-16 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="font-display text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent">
            Select Business
          </h1>
          <p className="text-lg md:text-xl text-white/60 max-w-xl mx-auto">
            Choose a business to access its ordering system
          </p>
        </motion.div>

        {businesses.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <Store className="w-20 h-20 text-white/20 mx-auto mb-4" />
            <p className="text-white/40 text-lg">No businesses available</p>
          </motion.div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl w-full">
            {businesses.map((business, index) => {
              const Icon = businessTypeIcons[business.type] || Store
              const gradient = businessTypeColors[business.type] || 'from-gray-400 to-gray-600'
              
              return (
                <motion.div
                  key={business.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <button
                    onClick={() => handleSelectBusiness(business)}
                    className="w-full text-left group"
                  >
                    <div className="glass-card p-6 hover:bg-white/10 transition-all duration-300 group-hover:scale-[1.02] group-hover:border-white/20">
                      <div className="flex items-center gap-4 mb-4">
                        <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
                          <Icon className="w-7 h-7 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h2 className="font-display text-xl font-semibold text-white truncate">
                            {business.name}
                          </h2>
                          <p className="text-sm text-white/40 capitalize">
                            {business.type}
                          </p>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm text-white/50">
                        {business.contactPhone && (
                          <p>{business.contactPhone}</p>
                        )}
                        {business.timings && (
                          <p>{business.timings}</p>
                        )}
                      </div>

                      <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between">
                        <span className="text-xs text-white/30 uppercase tracking-wider">
                          {business.paymentFlow === 'pre_service' ? 'Pay First' : 'Pay Later'}
                        </span>
                        <span className="text-brand-400 font-medium text-sm group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                          Select <span>→</span>
                        </span>
                      </div>
                    </div>
                  </button>
                </motion.div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
