/**
 * App.jsx – Enrutamiento principal de la aplicación.
 *
 * Tarea 13.1 – Integra CartProvider y Navbar con badge del carrito.
 * Tarea 15 – Integra ToastProvider para feedback visual (RNF-008.3).
 */

import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import {
  ForgotPasswordPage,
  LoginPage,
  RegisterPage,
} from './modules/auth/AuthModule';
import AuthRedirect from './modules/auth/components/AuthRedirect';
import {
  CatalogPage,
  ProductDetailPage,
  ProducerProfilePage,
} from './modules/catalog';
import CartModule from './modules/cart';
import CheckoutModule from './modules/checkout/CheckoutModule';
import ProducerModule from './modules/producer';
import OrderModule, { OrderDetailPage } from './modules/orders';
import ConsumerProfilePage from './modules/profile/ConsumerProfilePage';
import OrigenPage from './modules/origen/OrigenPage';
import ProductoresPage from './modules/productores/ProductoresPage';

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <CartProvider>
          <ToastProvider>
            <AppRoutes />
          </ToastProvider>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

/**
 * Rutas de la aplicación.
 * Separado de App para poder usar hooks de contexto (useAuth, useCart) dentro.
 */
function AppRoutes() {
  return (
    <>
      {/* Navbar global con badge del carrito (RNF-008.1, Req. 12.4) */}
      <Navbar />

      <Routes>
        {/* Ruta raíz – redirige a Origen */}
        <Route path="/" element={<Navigate to="/origen" replace />} />

        {/* Autenticación (públicas) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/auth/redirect" element={<AuthRedirect />} />

        {/* Catálogo (público) */}
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/catalog/:productId" element={<ProductDetailPage />} />
        <Route path="/producers/:producerId" element={<ProducerProfilePage />} />

        {/* Origen (público) */}
        <Route path="/origen" element={<OrigenPage />} />

        {/* Productores (público) */}
        <Route path="/productores" element={<ProductoresPage />} />

        {/* Carrito (CONSUMER – requiere autenticación) */}
        <Route
          path="/cart"
          element={
            <ProtectedRoute allowedRoles={['CONSUMER']}>
              <CartModule />
            </ProtectedRoute>
          }
        />

        {/* Checkout (CONSUMER – requiere autenticación) */}
        <Route
          path="/checkout"
          element={
            <ProtectedRoute allowedRoles={['CONSUMER']}>
              <CheckoutModule />
            </ProtectedRoute>
          }
        />

        {/* Pedidos (CONSUMER – requiere autenticación) */}
        <Route
          path="/orders"
          element={
            <ProtectedRoute allowedRoles={['CONSUMER']}>
              <OrderModule />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders/:orderId"
          element={
            <ProtectedRoute allowedRoles={['CONSUMER']}>
              <OrderDetailPage />
            </ProtectedRoute>
          }
        />

        {/* Perfil del consumidor */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute allowedRoles={['CONSUMER']}>
              <ConsumerProfilePage />
            </ProtectedRoute>
          }
        />

        {/* Panel del productor (PRODUCER – requiere autenticación) */}
        <Route
          path="/producer"
          element={
            <ProtectedRoute allowedRoles={['PRODUCER']}>
              <ProducerModule />
            </ProtectedRoute>
          }
        />
        <Route
          path="/producer/dashboard"
          element={
            <ProtectedRoute allowedRoles={['PRODUCER']}>
              <ProducerModule />
            </ProtectedRoute>
          }
        />
        <Route
          path="/producer/products"
          element={
            <ProtectedRoute allowedRoles={['PRODUCER']}>
              <ProducerModule />
            </ProtectedRoute>
          }
        />
        <Route
          path="/producer/sales"
          element={
            <ProtectedRoute allowedRoles={['PRODUCER']}>
              <ProducerModule />
            </ProtectedRoute>
          }
        />

        {/* Acceso no autorizado */}
        <Route path="/unauthorized" element={<PlaceholderPage title="Acceso no autorizado" />} />

        {/* 404 */}
        <Route path="*" element={<PlaceholderPage title="Página no encontrada" />} />
      </Routes>
    </>
  );
}

/**
 * Componente temporal para rutas no implementadas aún.
 * Se reemplazará por los módulos reales en tareas posteriores.
 */
function PlaceholderPage({ title }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 64px)',
        fontFamily: 'Inter, sans-serif',
        backgroundColor: '#F7F5F2',
        color: '#1F2937',
      }}
    >
      <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{title}</h1>
      <p style={{ color: '#6B7280' }}>Módulo en construcción</p>
    </div>
  );
}

export default App;
