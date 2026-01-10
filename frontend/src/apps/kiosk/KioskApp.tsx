import { Routes, Route } from 'react-router-dom'
import MenuPage from './pages/MenuPage'
import CartPage from './pages/CartPage'
import OrderConfirmation from './pages/OrderConfirmation'
import KioskLayout from './components/KioskLayout'

export default function KioskApp() {
  return (
    <KioskLayout>
      <Routes>
        <Route path="/" element={<MenuPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/order/:orderNumber" element={<OrderConfirmation />} />
      </Routes>
    </KioskLayout>
  )
}

