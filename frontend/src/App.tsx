import { Routes, Route, Navigate } from 'react-router-dom'
import KioskApp from './apps/kiosk/KioskApp'
import AdminApp from './apps/admin/AdminApp'
import BusinessSelectionPage from './pages/BusinessSelectionPage'
import InterfaceSelectionPage from './pages/InterfaceSelectionPage'
import ResourceSelectionPage from './pages/ResourceSelectionPage'
import LoginPage from './pages/LoginPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<BusinessSelectionPage />} />
      <Route path="/business/:businessId" element={<InterfaceSelectionPage />} />
      <Route path="/business/:businessId/resources" element={<ResourceSelectionPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/kiosk/*" element={<KioskApp />} />
      <Route path="/admin/*" element={<AdminApp />} />
      <Route path="/kitchen/*" element={<AdminApp />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
