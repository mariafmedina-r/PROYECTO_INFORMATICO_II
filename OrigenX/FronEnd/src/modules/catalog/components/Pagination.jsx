/**
 * components/Pagination.jsx – Componente de paginación accesible.
 *
 * Tarea 12.1 – Requerimiento: 9.4
 *
 * Muestra controles de paginación con navegación por teclado (RNF-002.4).
 * Implementa el patrón ARIA para navegación de paginación.
 */

import styles from '../catalog.module.css';

/**
 * Genera el rango de páginas a mostrar con elipsis.
 *
 * @param {number} currentPage
 * @param {number} totalPages
 * @returns {(number|'...')[]}
 */
function getPageRange(currentPage, totalPages) {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const pages = [];
  pages.push(1);

  if (currentPage > 3) pages.push('...');

  const start = Math.max(2, currentPage - 1);
  const end = Math.min(totalPages - 1, currentPage + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (currentPage < totalPages - 2) pages.push('...');

  pages.push(totalPages);

  return pages;
}

/**
 * @param {Object} props
 * @param {number} props.currentPage - Página actual (1-indexed).
 * @param {number} props.totalPages - Total de páginas.
 * @param {(page: number) => void} props.onPageChange - Callback al cambiar de página.
 */
export default function Pagination({ currentPage, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  const pageRange = getPageRange(currentPage, totalPages);

  return (
    <nav
      className={styles.pagination}
      aria-label="Paginación del catálogo"
      role="navigation"
    >
      {/* Anterior */}
      <button
        type="button"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={styles.paginationButton}
        aria-label="Página anterior"
      >
        ← Anterior
      </button>

      {/* Páginas */}
      {pageRange.map((page, index) =>
        page === '...' ? (
          <span
            key={`ellipsis-${index}`}
            className={styles.paginationEllipsis}
            aria-hidden="true"
          >
            …
          </span>
        ) : (
          <button
            key={page}
            type="button"
            onClick={() => onPageChange(page)}
            className={`${styles.paginationButton} ${
              page === currentPage ? styles.paginationButtonActive : ''
            }`}
            aria-label={`Página ${page}`}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        ),
      )}

      {/* Siguiente */}
      <button
        type="button"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={styles.paginationButton}
        aria-label="Página siguiente"
      >
        Siguiente →
      </button>
    </nav>
  );
}
