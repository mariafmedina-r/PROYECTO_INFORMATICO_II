/**
 * components/ProtectedRoute.jsx – Componente de ruta protegida.
 *
 * Redirige al login si el usuario no está autenticado (Req. 12.5).
 * Opcionalmente verifica que el usuario tenga el rol requerido.
 *
 * Tarea 2.9 – Requerimientos: 3.2, 3.3, 12.5
 */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Ruta protegida que requiere autenticación.
 *
 * @param {React.ReactNode} children - Componente a renderizar si el usuario está autenticado.
 * @param {string[]} [allowedRoles] - Roles permitidos. Si se omite, cualquier usuario autenticado puede acceder.
 * @returns {React.ReactNode}
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, userRole, loading } = useAuth();
  const location = useLocation();

  // Mientras se verifica el estado de auth, no redirigir aún
  if (loading) {
    return null;
  }

  // Si no está autenticado, redirigir al login guardando la ruta de origen (Req. 12.5)
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Si se especifican roles y el usuario no tiene el rol requerido
  // → redirigir al catálogo (no a /unauthorized, que confunde al usuario)
  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    return <Navigate to="/catalog" replace />;
  }

  return children;
}
