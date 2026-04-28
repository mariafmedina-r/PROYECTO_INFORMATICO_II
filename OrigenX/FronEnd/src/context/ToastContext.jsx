/**
 * context/ToastContext.jsx – Contexto global de notificaciones toast.
 *
 * Tarea 15 – RNF-008.3
 *
 * Provee la función `showToast(message, type)` a toda la aplicación.
 * Los toasts se auto-descartan después de 4 segundos.
 *
 * Tipos soportados: 'success' | 'error' | 'info' | 'warning'
 */

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from 'react';
import Toast from '../components/Toast';

const ToastContext = createContext(null);

/**
 * Proveedor del contexto de toasts.
 * Debe envolver la aplicación (dentro de BrowserRouter).
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const counterRef = useRef(0);

  /**
   * Muestra un toast.
   *
   * @param {string} message - Mensaje a mostrar.
   * @param {'success'|'error'|'info'|'warning'} [type='info'] - Tipo de toast.
   * @param {number} [duration=4000] - Duración en ms antes de auto-descartar.
   */
  const showToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++counterRef.current;
    setToasts((prev) => [...prev, { id, message, type, duration }]);
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Contenedor de toasts – fuera del flujo normal */}
      <div
        aria-live="polite"
        aria-atomic="false"
        aria-relevant="additions"
        style={{
          position: 'fixed',
          bottom: '1.5rem',
          right: '1.5rem',
          zIndex: 'var(--z-toast)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
          maxWidth: '400px',
          width: 'calc(100vw - 3rem)',
          pointerEvents: 'none',
        }}
      >
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            id={toast.id}
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onDismiss={dismissToast}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

/**
 * Hook para mostrar toasts desde cualquier componente.
 *
 * @returns {{ showToast: Function }}
 * @throws {Error} Si se usa fuera de ToastProvider.
 */
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast debe usarse dentro de un ToastProvider');
  }
  return context;
}

export default ToastContext;
