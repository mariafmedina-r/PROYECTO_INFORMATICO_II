/**
 * components/LoadingSpinner.jsx – Indicador de carga accesible.
 *
 * Tarea 15 – RNF-008.3
 *
 * - role="status" + aria-live="polite" para lectores de pantalla
 * - Tamaños: 'sm' (24px), 'md' (40px, default), 'lg' (64px)
 * - Puede mostrarse inline o centrado en un contenedor
 *
 * @param {{ size?: 'sm'|'md'|'lg', label?: string, centered?: boolean }} props
 */

import styles from './shared.module.css';

export default function LoadingSpinner({
  size = 'md',
  label = 'Cargando…',
  centered = false,
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={label}
      className={`${styles.spinnerWrapper} ${centered ? styles.spinnerCentered : ''}`}
    >
      <span
        className={`${styles.spinner} ${styles[`spinner_${size}`]}`}
        aria-hidden="true"
      />
      {/* Texto visible solo para lectores de pantalla */}
      <span className={styles.srOnly}>{label}</span>
    </div>
  );
}
