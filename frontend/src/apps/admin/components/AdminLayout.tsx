import { ReactNode } from 'react'
import { Link, useLocation, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LayoutDashboard, ClipboardList, Users, LogOut, User, ArrowLeft, Sofa } from 'lucide-react'
import { useAuthStore, useAdminStore } from '@/lib/store'

interface AdminLayoutProps {
  children: ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const businessParam = searchParams.get('business')
  const { businessId } = useAdminStore()
  const { user, isAdminOf, logout } = useAuthStore()

  const currentBusinessId = businessParam || businessId
  const isAdmin = isAdminOf(currentBusinessId)

  const navItems = [
    { path: `/admin?business=${currentBusinessId}`, icon: LayoutDashboard, label: 'Dashboard', match: '/admin' },
    { path: `/admin/orders?business=${currentBusinessId}`, icon: ClipboardList, label: 'Orders', match: '/admin/orders' },
    { path: `/admin/resources?business=${currentBusinessId}`, icon: Sofa, label: 'Resources', match: '/admin/resources' },
    ...(isAdmin ? [{ path: `/admin/team?business=${currentBusinessId}`, icon: Users, label: 'Team', match: '/admin/team' }] : []),
  ]

  const isActive = (match: string) => location.pathname === match

  return (
    <div className="min-h-screen bg-surface-950 flex">
      <aside className="w-64 border-r border-white/10 flex flex-col">
        <div className="p-6 border-b border-white/10">
          <Link to={`/business/${currentBusinessId}`} className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <div>
              <span className="font-display text-lg font-semibold block">Admin Panel</span>
              <span className="text-white/40 text-xs">Agentic Assist</span>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const active = isActive(item.match)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all relative ${active
                  ? 'text-white'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
                  }`}
              >
                {active && (
                  <motion.div
                    layoutId="nav-active"
                    className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-emerald-600/10 rounded-xl border border-emerald-500/30"
                  />
                )}
                <item.icon className="w-5 h-5 relative z-10" />
                <span className="relative z-10">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-white/10">
          {user && (
            <div className="mb-4 px-4 py-3 bg-white/5 rounded-xl">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-500/20 flex items-center justify-center">
                  <User className="w-4 h-4 text-brand-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{user.name}</p>
                  <p className="text-xs text-white/40 truncate">{user.email}</p>
                </div>
              </div>
              {isAdmin && (
                <div className="mt-2 px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded text-center">
                  Admin
                </div>
              )}
            </div>
          )}

          <Link
            to={`/business/${currentBusinessId}`}
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-white/60 hover:text-white hover:bg-white/5 transition-all w-full"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Business</span>
          </Link>
          <button
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-white/60 hover:text-red-400 hover:bg-red-500/10 transition-all w-full"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
