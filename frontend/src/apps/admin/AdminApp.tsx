import { Routes, Route } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import OrdersPage from './pages/OrdersPage'
import AdminLayout from './components/AdminLayout'

export default function AdminApp() {
  return (
    <AdminLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/orders" element={<OrdersPage />} />
      </Routes>
    </AdminLayout>
  )
}

