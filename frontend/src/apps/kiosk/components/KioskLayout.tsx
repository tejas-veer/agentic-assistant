import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ShoppingCart, Mic, Sparkles, X } from 'lucide-react'
import { useKioskStore } from '@/lib/store'
import VoiceAssistant from './VoiceAssistant'

interface KioskLayoutProps {
  children: ReactNode
}

export default function KioskLayout({ children }: KioskLayoutProps) {
  const location = useLocation()
  const { cart, isVoiceActive, setVoiceActive } = useKioskStore()
  const itemCount = cart?.items.reduce((sum, item) => sum + item.quantity, 0) || 0

  return (
    <div className="min-h-screen bg-surface-950 relative">
      <div 
        className="fixed inset-0 opacity-60 pointer-events-none"
        style={{ background: 'var(--gradient-mesh)' }}
      />

      <header className="fixed top-0 left-0 right-0 z-50 bg-surface-950/95 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/kiosk" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <span className="font-display text-xl font-semibold">Order Here</span>
          </Link>

          <Link to="/kiosk/cart" className="relative">
            <motion.div
              whileTap={{ scale: 0.95 }}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-all"
            >
              <ShoppingCart className="w-5 h-5" />
              {itemCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-brand-500 rounded-full text-xs font-bold flex items-center justify-center"
                >
                  {itemCount}
                </motion.span>
              )}
            </motion.div>
          </Link>
        </div>
      </header>

      <main className="relative z-10 pt-24 pb-32">
        {children}
      </main>

      {location.pathname === '/kiosk' && itemCount > 0 && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="fixed bottom-0 left-0 right-0 z-40 p-4 bg-surface-950/95 backdrop-blur-xl border-t border-white/5"
        >
          <div className="max-w-7xl mx-auto pr-24">
            <Link to="/kiosk/cart" className="block">
              <div className="btn-primary flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <ShoppingCart className="w-5 h-5" />
                  <span>View Cart ({itemCount} items)</span>
                </div>
                <span className="font-bold">₹{cart?.total.toFixed(0)}</span>
              </div>
            </Link>
          </div>
        </motion.div>
      )}

      <AnimatePresence>
        {!isVoiceActive && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <motion.button
              onClick={() => setVoiceActive(true)}
              className="group relative"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-brand-400 to-pink-500 rounded-full blur-lg opacity-60 group-hover:opacity-80 transition-opacity animate-pulse" />
              
              <div className="relative flex items-center gap-3 bg-gradient-to-r from-brand-400 to-pink-500 text-white pl-5 pr-6 py-4 rounded-full shadow-2xl shadow-brand-500/30">
                <div className="relative">
                  <Mic className="w-6 h-6" />
                  <Sparkles className="w-3 h-3 absolute -top-1 -right-1 text-yellow-300" />
                </div>
                <div className="text-left">
                  <span className="font-semibold block text-sm">Voice Order</span>
                  <span className="text-white/80 text-xs">Tap to speak</span>
                </div>
              </div>
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isVoiceActive && <VoiceAssistant />}
      </AnimatePresence>
    </div>
  )
}

