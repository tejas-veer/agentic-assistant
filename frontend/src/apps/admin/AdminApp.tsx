import { useEffect } from 'react'
import { Routes, Route, useSearchParams, useNavigate } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import OrdersPage from './pages/OrdersPage'
import TeamPage from './pages/TeamPage'
import AdminLayout from './components/AdminLayout'
import { useAdminStore, useAuthStore, DEFAULT_BUSINESS_ID } from '../../lib/store'

export default function AdminApp() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const setBusinessId = useAdminStore((s) => s.setBusinessId)
  const businessId = useAdminStore((s) => s.businessId)
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    const urlBusinessId = searchParams.get('business')
    if (urlBusinessId) {
      setBusinessId(urlBusinessId)
    } else if (!businessId || businessId === DEFAULT_BUSINESS_ID) {
      navigate('/')
      return
    }

    if (!isAuthenticated) {
      navigate(`/login?business=${urlBusinessId || businessId}&redirect=/admin?business=${urlBusinessId || businessId}`)
    }
  }, [searchParams, setBusinessId, businessId, navigate, isAuthenticated])

  if (!isAuthenticated) {
    return null
  }

  return (
    <AdminLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/team" element={<TeamPage />} />
      </Routes>
    </AdminLayout>
  )
}
