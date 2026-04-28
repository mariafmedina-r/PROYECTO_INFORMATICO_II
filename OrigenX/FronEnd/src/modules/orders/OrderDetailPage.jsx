/**
 * OrderDetailPage.jsx – Detalle de un pedido del consumidor.
 */

import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useOrderDetail } from './hooks/useOrderDetail';
import styles from './orders.module.css';

/* ── Lightbox ── */
function Lightbox({ src, alt, onClose }) {
  return (
    <div
      className={styles.lightboxOverlay}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Vista ampliada: ${alt}`}
    >
      <button
        type="button"
        className={styles.lightboxClose}
        onClick={onClose}
        aria-label="Cerrar vista ampliada"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
        </svg>
      </button>
      <div className={styles.lightboxContent} onClick={e => e.stopPropagation()}>
        <img src={src} alt={alt} className={styles.lightboxImg} />
      </div>
    </div>
  );
}

function formatPrice(price) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(price);
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
}

function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function StatusBadge({ status }) {
  const labels = { pendiente: 'Pendiente', pagado: 'Pagado', en_preparacion: 'En preparación', enviado: 'Enviado', entregado: 'Entregado', cancelado: 'Cancelado' };
  return <span className={`${styles.statusBadge} ${styles[`status_${status}`] ?? ''}`}>{labels[status] ?? status}</span>;
}

/* ── Línea de tiempo del estado ── */
const STATUS_STEPS = ['pendiente', 'pagado', 'en_preparacion', 'enviado', 'entregado'];

function StatusTimeline({ status }) {
  const currentIdx = STATUS_STEPS.indexOf(status);
  const isCancelled = status === 'cancelado';
  return (
    <div className={styles.timeline} aria-label="Estado del pedido">
      {STATUS_STEPS.map((step, i) => {
        const done = !isCancelled && i <= currentIdx;
        const active = !isCancelled && i === currentIdx;
        const labels = { pendiente: 'Pendiente', pagado: 'Pagado', en_preparacion: 'En preparación', enviado: 'Enviado', entregado: 'Entregado' };
        return (
          <div key={step} className={styles.timelineStep}>
            <div className={`${styles.timelineDot} ${done ? styles.timelineDotDone : ''} ${active ? styles.timelineDotActive : ''}`}>
              {done && !active ? (
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
              ) : null}
            </div>
            {i < STATUS_STEPS.length - 1 && (
              <div className={`${styles.timelineConnector} ${done && i < currentIdx ? styles.timelineConnectorDone : ''}`} />
            )}
            <span className={`${styles.timelineLabel} ${active ? styles.timelineLabelActive : ''}`}>{labels[step]}</span>
          </div>
        );
      })}
    </div>
  );
}

export default function OrderDetailPage() {
  const { orderId } = useParams();
  const { isConsumer } = useAuth();
  const { order, loading, error, refetch } = useOrderDetail(orderId);
  const [lightbox, setLightbox] = useState(null); // { src, alt }

  if (!isConsumer) {
    return (
      <div className={styles.accessDenied} role="alert">
        <span className={styles.accessDeniedIcon} aria-hidden="true">🔒</span>
        <h1 className={styles.accessDeniedTitle}>Acceso restringido</h1>
        <p className={styles.accessDeniedText}>Esta sección es exclusiva para consumidores.</p>
      </div>
    );
  }

  return (
    <main className={styles.detailPage}>
      <div className={styles.detailContainer}>

        {loading && (
          <div className={styles.loadingState} aria-busy="true">
            {[1,2,3].map(i => <div key={i} className={styles.skeletonCard} aria-hidden="true" />)}
          </div>
        )}

        {!loading && error && (
          <div className={styles.errorState} role="alert">
            <span className={styles.errorStateIcon}>⚠️</span>
            <h2 className={styles.errorStateTitle}>Error al cargar el pedido</h2>
            <p className={styles.errorStateText}>{error}</p>
            <button type="button" className={styles.retryButton} onClick={refetch}>Intentar nuevamente</button>
          </div>
        )}

        {!loading && !error && order && (
          <>
            {/* ── Encabezado ── */}
            <div className={styles.detailHeader}>
              <div>
                <h1 className={styles.detailTitle}>Pedido #{order.id?.slice(-8)}</h1>
                <p className={styles.detailDate}>{formatDateTime(order.createdAt ?? order.created_at)}</p>
                <Link to="/orders" className={styles.backLink} style={{ marginTop: 'var(--spacing-2)', display: 'inline-flex' }}>← Mis pedidos</Link>
              </div>
              <StatusBadge status={order.status} />
            </div>

            {/* ── Línea de tiempo ── */}
            <div className={styles.detailSection}>
              <StatusTimeline status={order.status} />
            </div>

            {/* ── Información clave ── */}
            <div className={styles.detailInfoGrid}>
              {/* Fecha de pago */}
              <div className={styles.infoCard}>
                <div className={styles.infoCardIcon}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>
                </div>
                <div>
                  <p className={styles.infoCardLabel}>Fecha de pago</p>
                  <p className={styles.infoCardValue}>
                    {order.status === 'pendiente' ? 'Pendiente de pago' : formatDate(order.updatedAt ?? order.updated_at)}
                  </p>
                </div>
              </div>

              {/* Mensajería */}
              <div className={styles.infoCard}>
                <div className={styles.infoCardIcon}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v3"/><rect width="7" height="7" x="14" y="11" rx="1"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>
                </div>
                <div>
                  <p className={styles.infoCardLabel}>Mensajería</p>
                  <p className={styles.infoCardValue}>{order.shippingCompany ?? '—'}</p>
                </div>
              </div>

              {/* Fecha estimada de entrega */}
              <div className={styles.infoCard}>
                <div className={styles.infoCardIcon}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
                </div>
                <div>
                  <p className={styles.infoCardLabel}>Entrega estimada</p>
                  <p className={styles.infoCardValue}>{order.estimatedDelivery ? formatDate(order.estimatedDelivery) : '—'}</p>
                </div>
              </div>

              {/* Ticket de seguimiento */}
              <div className={styles.infoCard}>
                <div className={styles.infoCardIcon}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 17v2"/><path d="M13 11v2"/></svg>
                </div>
                <div>
                  <p className={styles.infoCardLabel}>Ticket de seguimiento</p>
                  <p className={styles.infoCardValue} style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    {order.transactionId ?? 'Disponible al despachar'}
                  </p>
                </div>
              </div>
            </div>

            {/* ── Productos ── */}
            <section className={styles.detailSection} aria-label="Productos del pedido">
              <h2 className={styles.detailSectionTitle}>Productos</h2>
              <div className={styles.productList}>
                {(order.items ?? []).map((item, idx) => (
                  <div key={item.id ?? idx} className={styles.productRow}>
                    {/* Miniatura — clic abre lightbox */}
                    <div className={styles.productThumb}>
                      {item.mainImageUrl ? (
                        <button
                          type="button"
                          className={styles.productThumbBtn}
                          onClick={() => setLightbox({ src: item.mainImageUrl, alt: item.productNameSnapshot ?? item.name })}
                          aria-label={`Ver imagen ampliada de ${item.productNameSnapshot ?? item.name}`}
                        >
                          <img src={item.mainImageUrl} alt={item.productNameSnapshot ?? item.name} className={styles.productThumbImg} loading="lazy" />
                        </button>
                      ) : (
                        <div className={styles.productThumbPlaceholder} aria-hidden="true">
                          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>
                            <line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/>
                          </svg>
                        </div>
                      )}
                    </div>
                    {/* Info */}
                    <div className={styles.productInfo}>
                      <p className={styles.productName}>{item.productNameSnapshot ?? item.name}</p>
                      <p className={styles.productMeta}>{formatPrice(item.priceSnapshot ?? item.price)} / unidad · {item.quantity} {item.quantity === 1 ? 'unidad' : 'unidades'}</p>
                    </div>
                    {/* Subtotal */}
                    <p className={styles.productSubtotal}>
                      {formatPrice((item.priceSnapshot ?? item.price) * item.quantity)}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* ── Dirección + Resumen ── */}
            <div className={styles.detailBottomGrid}>
              {order.addressSnapshot && (
                <section className={styles.detailSection} aria-label="Dirección de envío">
                  <h2 className={styles.detailSectionTitle}>Dirección de envío</h2>
                  <div className={styles.addressBlock}>
                    <div className={styles.addressIconBox}>
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
                    </div>
                    <address style={{ fontStyle: 'normal' }}>
                      <strong>{order.addressSnapshot.street}</strong><br />
                      {order.addressSnapshot.city}, {order.addressSnapshot.department}
                      {order.addressSnapshot.postalCode && <> – CP {order.addressSnapshot.postalCode}</>}
                    </address>
                  </div>
                </section>
              )}

              <section className={styles.detailSection} aria-label="Resumen de costos">
                <h2 className={styles.detailSectionTitle}>Resumen</h2>
                <div className={styles.costSummary}>
                  <div className={styles.costRow}>
                    <span>Subtotal productos</span>
                    <span>{formatPrice(order.total - (order.shippingCost ?? 0))}</span>
                  </div>
                  {order.shippingCost != null && (
                    <div className={styles.costRow}>
                      <span>Envío ({order.shippingCompany})</span>
                      <span>{formatPrice(order.shippingCost)}</span>
                    </div>
                  )}
                  <hr className={styles.costDivider} />
                  <div className={styles.costTotal}>
                    <span>Total</span>
                    <span className={styles.costTotalAmount}>{formatPrice(order.total)}</span>
                  </div>
                </div>
              </section>
            </div>
          </>
        )}
      </div>
      {/* Lightbox */}
      {lightbox && (
        <Lightbox src={lightbox.src} alt={lightbox.alt} onClose={() => setLightbox(null)} />
      )}
    </main>
  );
}
