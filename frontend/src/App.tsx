import { Routes, Route, Navigate } from 'react-router-dom'
import KioskApp from './apps/kiosk/KioskApp'
import AdminApp from './apps/admin/AdminApp'
import LandingPage from './pages/LandingPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/kiosk/*" element={<KioskApp />} />
      <Route path="/admin/*" element={<AdminApp />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

