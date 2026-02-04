import { useEffect } from 'react'
import { Routes, Route, useSearchParams, useNavigate } from 'react-router-dom'
import MenuPage from './pages/MenuPage'
import CartPage from './pages/CartPage'
import OrderConfirmation from './pages/OrderConfirmation'
import KioskLayout from './components/KioskLayout'
import { useKioskStore, DEFAULT_BUSINESS_ID } from '../../lib/store'

export default function KioskApp() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { businessId, setBusinessId, setCartId, setCart } = useKioskStore()

  useEffect(() => {
    const urlBusinessId = searchParams.get('business')
    if (urlBusinessId) {
      // If switching to a different business, clear the cart
      if (urlBusinessId !== businessId) {
        setCartId(null)
        setCart(null)
      }
      setBusinessId(urlBusinessId)
    } else if (!businessId) {
      // Only redirect if no business ID is set at all
      navigate('/')
    }
    // If businessId exists (including DEFAULT_BUSINESS_ID), allow access
  }, [searchParams, setBusinessId, businessId, navigate, setCartId, setCart])

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
