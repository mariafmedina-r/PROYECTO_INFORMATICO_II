/**
 * OrderModule.jsx – Historial de pedidos del consumidor.
 *
 * Tarea 14.2 – Requerimientos: 15.1, 15.2, 15.3
 *
 * Lista los pedidos del consumidor ordenados por fecha descendente.
 * Solo accesible para usuarios con rol CONSUMER.
 */

import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useOrders } from './hooks/useOrders';
import styles from './orders.module.css';

/** Formatea precio en COP */
function formatPrice(price) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
  }).format(price);
}

/** Formatea fecha legible */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  return date.toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/** Badge de estado del pedido */
function StatusBadge({ status }) {
  const labels = {
    pendiente: 'Pendiente',
    pagado: 'Pagado',
    en_preparacion: 'En preparación',
    enviado: 'Enviado',
    entregado: 'Entregado',
    cancelado: 'Cancelado',
  };
  return (
    <span className={`${styles.statusBadge} ${styles[`status_${status}`] ?? ''}`}>
      {labels[status] ?? status}
    </span>
  );
}

export default function OrderModule() {
  const { isConsumer } = useAuth();
  const { orders, loading, error, refetch } = useOrders();

  // Acceso denegado si no es consumidor
  if (!isConsumer) {
    return (
      <div className={styles.accessDenied} role="alert">
        <span className={styles.accessDeniedIcon} aria-hidden="true">🔒</span>
        <h1 className={styles.accessDeniedTitle}>Acceso restringido</h1>
        <p className={styles.accessDeniedText}>
          Esta sección es exclusiva para consumidores registrados.
        </p>
      </div>
    );
  }

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        {/* Encabezado */}
        <header className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>Mis Pedidos</h1>
          <p className={styles.pageSubtitle}>
            Historial de todos tus pedidos realizados.
          </p>
        </header>

        {/* Estado de carga */}
        {loading && (
          <div className={styles.loadingState} aria-busy="true" aria-label="Cargando pedidos">
            {[1, 2, 3].map((i) => (
              <div key={i} className={styles.skeletonCard} aria-hidden="true" />
            ))}
          </div>
        )}

        {/* Estado de error */}
        {!loading && error && (
          <div className={styles.errorState} role="alert">
            <span className={styles.errorStateIcon}>⚠️</span>
            <h2 className={styles.errorStateTitle}>Error al cargar los pedidos</h2>
            <p className={styles.errorStateText}>{error}</p>
            <button type="button" className={styles.retryButton} onClick={refetch}>
              Intentar nuevamente
            </button>
          </div>
        )}

        {/* Sin pedidos */}
        {!loading && !error && orders.length === 0 && (
          <div className={styles.emptyState} role="status">
            <span className={styles.emptyStateIcon} aria-hidden="true">📦</span>
            <h2 className={styles.emptyStateTitle}>Sin pedidos</h2>
            <p className={styles.emptyStateText}>
              Aún no has realizado ningún pedido. Explora el catálogo y encuentra tu café favorito.
            </p>
            <Link to="/catalog" className={styles.emptyStateButton}>
              Ir al catálogo
            </Link>
          </div>
        )}

        {/* Lista de pedidos */}
        {!loading && !error && orders.length > 0 && (
          <section
            className={styles.orderList}
            aria-label={`${orders.length} pedido${orders.length !== 1 ? 's' : ''}`}
          >
            {orders.map((order) => {
              const preview = order.itemsPreview ?? [];
              const firstItem = preview[0];
              return (
                <Link
                  key={order.id}
                  to={`/orders/${order.id}`}
                  className={styles.orderCard}
                  aria-label={`Pedido #${order.id?.slice(-8)}, ${formatDate(order.createdAt ?? order.created_at)}, total ${formatPrice(order.total)}, estado ${order.status}`}
                >
                  {/* Miniatura del primer producto */}
                  <div className={styles.orderThumb}>
                    {firstItem?.mainImageUrl ? (
                      <img src={firstItem.mainImageUrl} alt={firstItem.productNameSnapshot ?? ''} className={styles.orderThumbImg} loading="lazy" />
                    ) : (
                      <div className={styles.orderThumbPlaceholder} aria-hidden="true">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>
                          <line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/>
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Info principal */}
                  <div className={styles.orderCardLeft}>
                    <span className={styles.orderNumber}>#{order.id?.slice(-8) ?? order.id}</span>
                    <span className={styles.orderDate}>{formatDate(order.createdAt ?? order.created_at)}</span>
                    {preview.length > 0 && (
                      <span className={styles.orderProductNames}>
                        {preview.map(i => i.productNameSnapshot).filter(Boolean).join(' · ')}
                      </span>
                    )}
                  </div>

                  {/* Total + estado + flecha */}
                  <div className={styles.orderCardRight}>
                    <span className={styles.orderTotal}>{formatPrice(order.total)}</span>
                    <StatusBadge status={order.status} />
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={styles.orderChevron}>
                      <path d="m9 18 6-6-6-6"/>
                    </svg>
                  </div>
                </Link>
              );
            })}
          </section>
        )}
      </div>
    </main>
  );
}
