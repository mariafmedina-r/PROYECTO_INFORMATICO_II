/**
 * components/Toast.jsx – Notificación toast accesible.
 *
 * Tarea 15 – RNF-008.3
 *
 * - aria-live="assertive" para errores (interrupción inmediata)
 * - aria-live="polite" para éxito/info/warning (no interrumpe)
 * - Auto-descarte después de `duration` ms
 * - Botón de cierre manual con área mínima 44×44 px
 * - Animación de entrada/salida suave
 *
 * @param {{ id: number, message: string, type: string, duration: number, onDismiss: Function }} props
 */

import { useEffect, useRef, useState } from 'react';
import styles from './shared.module.css';

const TYPE_CONFIG = {
  success: {
    icon: '✓',
    label: 'Éxito',
    ariaLive: 'polite',
  },
  error: {
    icon: '✕',
    label: 'Error',
    ariaLive: 'assertive',
  },
  warning: {
    icon: '⚠',
    label: 'Advertencia',
    ariaLive: 'polite',
  },
  info: {
    icon: 'ℹ',
    label: 'Información',
    ariaLive: 'polite',
  },
};

export default function Toast({ id, message, type = 'info', duration = 4000, onDismiss }) {
  const [visible, setVisible] = useState(false);
  const timerRef = useRef(null);
  const config = TYPE_CONFIG[type] ?? TYPE_CONFIG.info;

  // Animación de entrada
  useEffect(() => {
    const enterTimer = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(enterTimer);
  }, []);

  // Auto-descarte
  useEffect(() => {
    if (duration <= 0) return;
    timerRef.current = setTimeout(() => handleDismiss(), duration);
    return () => clearTimeout(timerRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [duration]);

  const handleDismiss = () => {
    setVisible(false);
    // Esperar la animación de salida antes de eliminar del DOM
    setTimeout(() => onDismiss(id), 300);
  };

  return (
    <div
      role="status"
      aria-live={config.ariaLive}
      aria-atomic="true"
      aria-label={`${config.label}: ${message}`}
      className={`${styles.toast} ${styles[`toast_${type}`]} ${visible ? styles.toastVisible : ''}`}
      style={{ pointerEvents: 'all' }}
    >
      {/* Ícono */}
      <span className={styles.toastIcon} aria-hidden="true">
        {config.icon}
      </span>

      {/* Mensaje */}
      <p className={styles.toastMessage}>{message}</p>

      {/* Botón de cierre */}
      <button
        type="button"
        onClick={handleDismiss}
        className={styles.toastClose}
        aria-label="Cerrar notificación"
      >
        ×
      </button>
    </div>
  );
}
