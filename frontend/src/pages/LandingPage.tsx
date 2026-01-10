import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Monitor, Settings, Mic, Phone } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-950 relative overflow-hidden">
      <div 
        className="absolute inset-0 opacity-60"
        style={{ background: 'var(--gradient-mesh)' }}
      />
      
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h1 className="font-display text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent">
            Agentic Assist
          </h1>
          <p className="text-xl md:text-2xl text-white/60 max-w-2xl mx-auto">
            AI-powered ordering system with voice assistant, kiosk interface, and intelligent call agents
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl w-full">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Link to="/kiosk" className="block group">
              <div className="glass-card p-8 hover:bg-white/10 transition-all duration-300 group-hover:scale-[1.02] group-hover:border-brand-400/30">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
                    <Monitor className="w-7 h-7 text-white" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold">Customer Kiosk</h2>
                </div>
                <p className="text-white/60 mb-6">
                  Self-service ordering with intuitive touch interface and voice assistant support
                </p>
                <div className="flex items-center gap-2 text-brand-400 font-medium">
                  <span>Open Kiosk</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Link to="/admin" className="block group">
              <div className="glass-card p-8 hover:bg-white/10 transition-all duration-300 group-hover:scale-[1.02] group-hover:border-emerald-400/30">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
                    <Settings className="w-7 h-7 text-white" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold">Admin Panel</h2>
                </div>
                <p className="text-white/60 mb-6">
                  Manage orders, view analytics, and control menu items in real-time
                </p>
                <div className="flex items-center gap-2 text-emerald-400 font-medium">
                  <span>Open Dashboard</span>
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
          className="mt-16 flex flex-wrap justify-center gap-8 text-white/40"
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

