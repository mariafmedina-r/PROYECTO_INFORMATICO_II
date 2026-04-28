/**
 * AuthRedirect.jsx – Redirige al usuario según su rol tras el login.
 *
 * CONSUMER  → /catalog
 * PRODUCER  → /producer
 * ADMIN     → /catalog (fallback)
 *
 * Espera a que el rol esté disponible en el AuthContext antes de redirigir.
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';

export default function AuthRedirect() {
  const { userRole, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (loading) return; // esperar a que el rol esté listo

    if (userRole === 'PRODUCER') {
      navigate('/producer', { replace: true });
    } else {
      // CONSUMER, ADMIN o cualquier otro rol → catálogo
      navigate('/catalog', { replace: true });
    }
  }, [userRole, loading, navigate]);

  // Pantalla de espera mínima mientras carga el rol
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: '#F7F5F2',
      }}
      aria-busy="true"
      aria-label="Cargando..."
    >
      <div style={{ textAlign: 'center', color: '#6B7280', fontFamily: 'Inter, sans-serif' }}>
        <p>Cargando…</p>
      </div>
    </div>
  );
}
