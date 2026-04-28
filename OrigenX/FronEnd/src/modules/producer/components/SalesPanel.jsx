/**
 * components/SalesPanel.jsx – Panel de ventas del productor.
 *
 * Tarea 14.1 – Requerimientos: 16.1, 16.2, 16.3
 *
 * Muestra: pedidos con productos del productor, totales mensuales, filtro por fecha.
 */

import { useState } from 'react';
import { useSales } from '../hooks/useSales';
import styles from '../producer.module.css';

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
    month: 'short',
    day: 'numeric',
  });
}

/** Badge de estado del pedido */
function OrderStatusBadge({ status }) {
  const labels = {
    pendiente: 'Pendiente',
    pagado: 'Pagado',
    en_preparacion: 'En preparación',
    enviado: 'Enviado',
    entregado: 'Entregado',
    cancelado: 'Cancelado',
  };
  return (
    <span className={`${styles.orderStatusBadge} ${styles[`orderStatus_${status}`] ?? ''}`}>
      {labels[status] ?? status}
    </span>
  );
}

export default function SalesPanel() {
  const { sales, monthlySummary, loading, error, filterByDateRange } = useSales();
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');

  const handleFilter = (e) => {
    e.preventDefault();
    filterByDateRange(fromDate, toDate);
  };

  const handleClearFilter = () => {
    setFromDate('');
    setToDate('');
    filterByDateRange('', '');
  };

  if (loading) {
    return (
      <div className={styles.loadingState} aria-busy="true">
        {[1, 2, 3].map((i) => (
          <div key={i} className={styles.skeletonBlock} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState} role="alert">
        <span className={styles.errorStateIcon}>⚠️</span>
        <p className={styles.errorStateText}>{error}</p>
      </div>
    );
  }

  return (
    <section className={styles.salesSection}>
      <h2 className={styles.sectionTitle}>Mis Ventas</h2>

      {/* Resumen mensual */}
      <div className={styles.monthlySummary}>
        <div className={styles.summaryCard}>
          <p className={styles.summaryCardLabel}>Mes actual</p>
          <p className={styles.summaryCardValue}>
            {formatPrice(monthlySummary.currentMonth)}
          </p>
        </div>
        <div className={styles.summaryCard}>
          <p className={styles.summaryCardLabel}>Mes anterior</p>
          <p className={styles.summaryCardValue}>
            {formatPrice(monthlySummary.previousMonth)}
          </p>
        </div>
      </div>

      {/* Filtro por fecha */}
      <form
        className={styles.dateFilterForm}
        onSubmit={handleFilter}
        aria-label="Filtrar ventas por fecha"
      >
        <div className={styles.dateFilterGroup}>
          <label htmlFor="fromDate" className={styles.filterLabel}>
            Desde
          </label>
          <input
            id="fromDate"
            type="date"
            className={styles.filterInput}
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
          />
        </div>
        <div className={styles.dateFilterGroup}>
          <label htmlFor="toDate" className={styles.filterLabel}>
            Hasta
          </label>
          <input
            id="toDate"
            type="date"
            className={styles.filterInput}
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
          />
        </div>
        <button type="submit" className={styles.filterButton}>
          Filtrar
        </button>
        {(fromDate || toDate) && (
          <button
            type="button"
            className={styles.clearFilterButton}
            onClick={handleClearFilter}
          >
            Limpiar
          </button>
        )}
      </form>

      {/* Sin ventas */}
      {sales.length === 0 && (
        <div className={styles.emptyState} role="status">
          <span className={styles.emptyStateIcon}>📊</span>
          <h3 className={styles.emptyStateTitle}>Sin ventas</h3>
          <p className={styles.emptyStateText}>
            No hay ventas registradas en el período seleccionado.
          </p>
        </div>
      )}

      {/* Tabla de ventas — desktop */}
      {sales.length > 0 && (
        <div className={styles.salesTableWrapper}>
          <table className={styles.table} aria-label="Historial de ventas">
            <thead>
              <tr>
                <th className={styles.th}>Pedido</th>
                <th className={styles.th}>Fecha</th>
                <th className={styles.th}>Cliente</th>
                <th className={styles.th}>Productos</th>
                <th className={styles.th}>Total</th>
                <th className={styles.th}>Estado</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id} className={styles.tr}>
                  <td className={styles.td}>
                    <span className={styles.orderId}>#{sale.id?.slice(-8) ?? '—'}</span>
                  </td>
                  <td className={styles.td}>
                    {formatDate(sale.createdAt ?? sale.created_at)}
                  </td>
                  <td className={styles.td}>
                    {sale.consumerInfo ? (
                      <div className={styles.consumerInfo}>
                        <span className={styles.consumerName}>
                          {sale.consumerInfo.name ?? '—'}
                        </span>
                        {sale.consumerInfo.email && (
                          <span className={styles.consumerEmail}>
                            {sale.consumerInfo.email}
                          </span>
                        )}
                        {sale.addressSnapshot && (
                          <span className={styles.consumerAddress}>
                            {[
                              sale.addressSnapshot.street,
                              sale.addressSnapshot.city,
                              sale.addressSnapshot.department,
                            ]
                              .filter(Boolean)
                              .join(', ')}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span>—</span>
                    )}
                  </td>
                  <td className={styles.td}>
                    <ul className={styles.saleItemsList}>
                      {(sale.items ?? []).map((item, idx) => (
                        <li key={idx} className={styles.saleItem}>
                          {item.productNameSnapshot ?? item.name} ×{item.quantity}
                          {' — '}
                          {formatPrice((item.priceSnapshot ?? item.price) * item.quantity)}
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td className={styles.td}>
                    <span className={styles.saleTotal}>{formatPrice(sale.total)}</span>
                  </td>
                  <td className={styles.td}>
                    <OrderStatusBadge status={sale.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tarjetas de ventas — móvil */}
      {sales.length > 0 && (
        <div className={styles.saleCardList} aria-label="Historial de ventas">
          {sales.map((sale) => (
            <div key={sale.id} className={styles.saleCard}>
              {/* Encabezado: pedido + estado */}
              <div className={styles.saleCardHeader}>
                <span className={styles.orderId}>#{sale.id?.slice(-8) ?? '—'}</span>
                <OrderStatusBadge status={sale.status} />
              </div>

              {/* Fecha + total */}
              <div className={styles.saleCardMeta}>
                <span className={styles.saleCardDate}>
                  📅 {formatDate(sale.createdAt ?? sale.created_at)}
                </span>
                <span className={styles.saleTotal}>
                  {formatPrice(sale.total)}
                </span>
              </div>

              {/* Cliente */}
              {sale.consumerInfo && (
                <div className={styles.saleCardSection}>
                  <span className={styles.saleCardLabel}>Cliente</span>
                  <div className={styles.consumerInfo}>
                    <span className={styles.consumerName}>
                      {sale.consumerInfo.name ?? '—'}
                    </span>
                    {sale.consumerInfo.email && (
                      <span className={styles.consumerEmail}>
                        {sale.consumerInfo.email}
                      </span>
                    )}
                    {sale.addressSnapshot && (
                      <span className={styles.consumerAddress}>
                        {[
                          sale.addressSnapshot.street,
                          sale.addressSnapshot.city,
                          sale.addressSnapshot.department,
                        ]
                          .filter(Boolean)
                          .join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Productos */}
              <div className={styles.saleCardSection}>
                <span className={styles.saleCardLabel}>Productos</span>
                <ul className={styles.saleItemsList}>
                  {(sale.items ?? []).map((item, idx) => (
                    <li key={idx} className={styles.saleItem}>
                      {item.productNameSnapshot ?? item.name} ×{item.quantity}
                      {' — '}
                      {formatPrice((item.priceSnapshot ?? item.price) * item.quantity)}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
