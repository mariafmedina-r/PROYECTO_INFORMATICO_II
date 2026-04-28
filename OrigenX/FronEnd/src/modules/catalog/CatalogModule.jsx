/**
 * CatalogModule.jsx – Página principal del catálogo de productos.
 *
 * Tarea 12.1 – Requerimientos: 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5
 *
 * Muestra el listado de productos activos con:
 *   - Tarjetas con nombre, imagen (lazy loading), precio y nombre del Productor
 *   - Barra de búsqueda y filtros combinables (texto, precio, región)
 *   - Paginación de 20 productos por página
 *   - Mensaje cuando no hay resultados
 *   - Skeleton de carga y manejo de errores
 */

import { useCallback, useEffect, useState } from 'react';
import { useCatalog } from './hooks/useCatalog';
import ProductCard from './components/ProductCard';
import SearchFilterBar from './components/SearchFilterBar';
import Pagination from './components/Pagination';
import styles from './catalog.module.css';

const SKELETON_COUNT = 8;

/** Skeleton de carga para las tarjetas */
function SkeletonGrid() {
  return (
    <div className={styles.loadingGrid} aria-busy="true" aria-label="Cargando productos">
      {Array.from({ length: SKELETON_COUNT }).map((_, i) => (
        <div key={i} className={styles.skeletonCard} aria-hidden="true">
          <div className={styles.skeletonImage} />
          <div className={styles.skeletonBody}>
            <div className={styles.skeletonLine} />
            <div className={`${styles.skeletonLine} ${styles.skeletonLineShort}`} />
            <div className={`${styles.skeletonLine} ${styles.skeletonLinePrice}`} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function CatalogModule() {
  const [filters, setFilters] = useState({
    q: '',
    minPrice: '',
    maxPrice: '',
    region: '',
  });
  const [page, setPage] = useState(1);

  // Resetear a página 1 cuando cambian los filtros
  const handleFiltersChange = useCallback((newFilters) => {
    setFilters(newFilters);
    setPage(1);
  }, []);

  const { products, totalPages, totalItems, loading, error, refetch } = useCatalog(
    filters,
    page,
  );

  // Scroll al inicio al cambiar de página
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [page]);

  const hasActiveFilters =
    filters.q || filters.minPrice || filters.maxPrice || filters.region;

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        {/* Encabezado */}
        <header className={styles.catalogHeader}>
          <h1 className={styles.catalogTitle}>Catálogo de Cafés</h1>
          <p className={styles.catalogSubtitle}>
            Descubre cafés de origen colombiano directamente de los productores
          </p>
        </header>

        {/* Barra de búsqueda y filtros */}
        <SearchFilterBar
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />

        {/* Información de resultados */}
        {!loading && !error && (
          <p className={styles.resultsInfo} aria-live="polite" aria-atomic="true">
            {totalItems === 0
              ? 'Sin resultados'
              : `${totalItems} producto${totalItems !== 1 ? 's' : ''} encontrado${totalItems !== 1 ? 's' : ''}`}
            {hasActiveFilters && ' con los filtros aplicados'}
          </p>
        )}

        {/* Estado de carga */}
        {loading && <SkeletonGrid />}

        {/* Estado de error */}
        {!loading && error && (
          <div className={styles.errorState} role="alert">
            <span className={styles.errorStateIcon} aria-hidden="true">⚠️</span>
            <h2 className={styles.errorStateTitle}>Error al cargar el catálogo</h2>
            <p className={styles.errorStateText}>{error}</p>
            <button type="button" onClick={refetch} className={styles.retryButton}>
              Intentar nuevamente
            </button>
          </div>
        )}

        {/* Sin resultados (Req. 10.4) */}
        {!loading && !error && products.length === 0 && (
          <div className={styles.emptyState} role="status" aria-live="polite">
            <span className={styles.emptyStateIcon} aria-hidden="true">☕</span>
            <h2 className={styles.emptyStateTitle}>No se encontraron productos</h2>
            <p className={styles.emptyStateText}>
              {hasActiveFilters
                ? 'No hay productos que coincidan con los criterios de búsqueda seleccionados. Intenta con otros filtros.'
                : 'Aún no hay productos disponibles en el catálogo.'}
            </p>
          </div>
        )}

        {/* Grid de productos */}
        {!loading && !error && products.length > 0 && (
          <>
            <section
              aria-label={`Productos, página ${page} de ${totalPages}`}
              className={styles.productGrid}
            >
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </section>

            {/* Paginación (Req. 9.4) */}
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </main>
  );
}
