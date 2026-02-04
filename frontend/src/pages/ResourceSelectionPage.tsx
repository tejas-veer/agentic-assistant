import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Loader2, AlertCircle, Users, CheckCircle2 } from 'lucide-react'
import { businessApi } from '../lib/api'
import { useKioskStore } from '../lib/store'
import type { Business, Resource } from '../lib/types'

export default function ResourceSelectionPage() {
  const { businessId } = useParams<{ businessId: string }>()
  const navigate = useNavigate()
  const { setBusinessId, setResource } = useKioskStore()
  
  const [business, setBusiness] = useState<Business | null>(null)
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [occupying, setOccupying] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (businessId) {
      loadData(businessId)
    }
  }, [businessId])

  const loadData = async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      const [businessData, resourcesData] = await Promise.all([
        businessApi.getById(id),
        businessApi.getAvailableResources(id)
      ])
      setBusiness(businessData)
      setResources(resourcesData)
    } catch (err) {
      console.error('Failed to load data:', err)
      setError('Failed to load resources')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectResource = async (resource: Resource) => {
    if (!businessId) return
    
    setOccupying(resource.id)
    try {
      await businessApi.occupyResource(resource.id)
      setBusinessId(businessId)
      setResource(resource.id, resource.name)
      navigate(`/kiosk?business=${businessId}`)
    } catch (err) {
      console.error('Failed to occupy resource:', err)
      setError('Failed to select resource. It may have been taken.')
      // Reload resources to get fresh data
      loadData(businessId)
    } finally {
      setOccupying(null)
    }
  }

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'table': return '🪑'
      case 'room': return '🚪'
      case 'slot': return '📅'
      default: return '📍'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-brand-400 animate-spin mx-auto mb-4" />
          <p className="text-white/60">Loading resources...</p>
        </div>
      </div>
    )
  }

  if (error && !business) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center px-6">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="font-display text-2xl font-semibold text-white mb-2">Error</h2>
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
      
      <div className="relative z-10 min-h-screen px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate(`/business/${businessId}`)}
            className="flex items-center gap-2 text-white/60 hover:text-white transition-colors mb-8"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="font-display text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent">
              Select Your {business?.resourceType || 'Table'}
            </h1>
            <p className="text-lg text-white/60">
              {business?.name} - Choose an available {business?.resourceType?.toLowerCase() || 'table'} to continue
            </p>
          </motion.div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-400 text-center"
            >
              {error}
            </motion.div>
          )}

          {resources.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-16"
            >
              <AlertCircle className="w-16 h-16 text-amber-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Available Resources</h3>
              <p className="text-white/60 mb-6">
                All {business?.resourceType?.toLowerCase() || 'table'}s are currently occupied. Please wait.
              </p>
              <button
                onClick={() => loadData(businessId!)}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium transition-colors"
              >
                Refresh
              </button>
            </motion.div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {resources.map((resource, i) => (
                <motion.button
                  key={resource.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => handleSelectResource(resource)}
                  disabled={occupying !== null}
                  className="glass-card p-6 hover:bg-white/10 hover:border-brand-400/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                  <div className="text-4xl mb-3">{getResourceIcon(resource.type)}</div>
                  <h3 className="font-display text-xl font-semibold mb-1">{resource.name}</h3>
                  {resource.capacity && (
                    <div className="flex items-center justify-center gap-1 text-white/60 text-sm">
                      <Users className="w-4 h-4" />
                      <span>{resource.capacity} seats</span>
                    </div>
                  )}
                  
                  {occupying === resource.id ? (
                    <div className="mt-4 flex items-center justify-center gap-2 text-brand-400">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Selecting...</span>
                    </div>
                  ) : (
                    <div className="mt-4 flex items-center justify-center gap-2 text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity">
                      <CheckCircle2 className="w-4 h-4" />
                      <span className="text-sm">Select</span>
                    </div>
                  )}
                </motion.button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
