import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LayoutDashboard, CheckCircle2, XCircle, Clock, Sofa, Armchair, AlertCircle, Loader2 } from 'lucide-react'
import { businessApi, type Resource } from '@/lib/api'
import { useAdminStore } from '@/lib/store'

export default function ResourcesPage() {
    const { businessId } = useAdminStore()
    const [resources, setResources] = useState<Resource[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        loadResources()
    }, [businessId])

    const loadResources = async () => {
        try {
            setLoading(true)
            const data = await businessApi.getResources(businessId)
            setResources(data || [])
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load resources')
        } finally {
            setLoading(false)
        }
    }

    const handleToggleStatus = async (resource: Resource) => {
        try {
            let updated
            if (resource.status === 'available') {
                updated = await businessApi.occupyResource(resource.id)
            } else {
                updated = await businessApi.freeResource(resource.id)
            }

            setResources(resources.map(r => r.id === resource.id ? updated : r))
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to update resource status')
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'available': return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30'
            case 'assigned':
            case 'occupied': return 'text-amber-400 bg-amber-500/20 border-amber-500/30'
            case 'maintenance': return 'text-red-400 bg-red-500/20 border-red-500/30'
            default: return 'text-white/60 bg-white/10 border-white/10'
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'available': return <CheckCircle2 className="w-4 h-4" />
            case 'assigned':
            case 'occupied': return <Clock className="w-4 h-4" />
            case 'maintenance': return <XCircle className="w-4 h-4" />
            default: return <AlertCircle className="w-4 h-4" />
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-12 h-12 text-brand-400 animate-spin" />
            </div>
        )
    }

    return (
        <div>
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="font-display text-3xl font-bold mb-2">Resource Management</h1>
                <p className="text-white/60">Manage your tables, rooms, and other resources</p>
            </motion.div>

            {error && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-400 flex items-center gap-3"
                >
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    {error}
                </motion.div>
            )}

            {resources.length === 0 ? (
                <div className="glass-card p-12 text-center text-white/40">
                    <Sofa className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No resources found for this business</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {resources.map((resource) => (
                        <motion.div
                            key={resource.id}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="glass-card p-4 relative group"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
                                        {resource.type === 'table' ? <Armchair className="w-5 h-5 text-brand-400" /> : <Sofa className="w-5 h-5 text-brand-400" />}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold">{resource.name}</h3>
                                        <p className="text-xs text-white/40 capitalize">{resource.type} • Capacity: {resource.capacity}</p>
                                    </div>
                                </div>

                                <button
                                    onClick={() => handleToggleStatus(resource)}
                                    className={`px-3 py-1.5 rounded-lg border text-xs font-medium flex items-center gap-2 transition-all ${getStatusColor(resource.status || 'available')}`}
                                >
                                    {getStatusIcon(resource.status || 'available')}
                                    <span className="capitalize">{resource.status}</span>
                                </button>
                            </div>

                            <div className="pt-4 border-t border-white/10 flex justify-between items-center">
                                <span className="text-xs text-white/40">Last updated: {new Date(resource.updatedAt || resource.createdAt).toLocaleTimeString()}</span>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    )
}
