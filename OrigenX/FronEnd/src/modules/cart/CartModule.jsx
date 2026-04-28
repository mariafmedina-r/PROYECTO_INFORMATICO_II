/**
 * CartModule.jsx – Página principal del carrito de compras.
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import apiClient from '../../config/axios';
import { formatPrice } from '../catalog/utils/formatPrice';
import styles from './cart.module.css';

const SKELETON_COUNT = 3;

/** Skeleton de carga */
function CartSkeleton() {
  return (
    <div className={styles.loadingState} aria-busy="true" aria-label="Cargando carrito">
      {Array.from({ length: SKELETON_COUNT }).map((_, i) => (
        <div key={i} className={styles.skeletonItem} aria-hidden="true" />
      ))}
    </div>
  );
}

/** Ítem individual del carrito */
function CartItem({ item, onUpdateQuantity, onRemove }) {
  const subtotal = (item.price ?? 0) * (item.quantity ?? 1);

  return (
    <article className={styles.cartItem} aria-label={`Ítem: ${item.product_name ?? item.productName}`}>
      {/* Imagen del producto */}
      <div className={styles.itemImageBox}>
        {item.imageUrl ? (
          <img src={item.imageUrl} alt={item.product_name ?? item.productName} className={styles.itemImage} loading="lazy" />
        ) : (
          <div className={styles.itemImagePlaceholder} aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>
              <line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/>
            </svg>
          </div>
        )}
      </div>

      {/* Información del producto */}
      <div className={styles.itemInfo}>
        <Link to={`/catalog/${item.product_id ?? item.productId}`} className={styles.itemName}>
          {item.product_name ?? item.productName}
        </Link>
        {item.producerName && (
          <p className={styles.itemProducer}>
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
              <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
            </svg>
            {item.producerName}
          </p>
        )}
        <p className={styles.itemUnitPrice}>{formatPrice(item.price)} / unidad</p>
      </div>

      {/* Controles de cantidad */}
      <div className={styles.quantityControls} role="group" aria-label={`Cantidad de ${item.product_name ?? item.productName}`}>
        <button type="button"
          onClick={() => item.quantity > 1 && onUpdateQuantity(item.id, item.quantity - 1)}
          disabled={item.quantity <= 1} className={styles.quantityButton} aria-label="Disminuir cantidad">
          −
        </button>
        <span className={styles.quantityValue} aria-live="polite">{item.quantity}</span>
        <button type="button"
          onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
          className={styles.quantityButton} aria-label="Aumentar cantidad">
          +
        </button>
      </div>

      {/* Subtotal */}
      <p className={styles.itemSubtotal} aria-label={`Subtotal: ${formatPrice(subtotal)}`}>
        {formatPrice(subtotal)}
      </p>

      {/* Eliminar */}
      <button type="button" onClick={() => onRemove(item.id)} className={styles.removeButton}
        aria-label={`Eliminar ${item.product_name ?? item.productName} del carrito`}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
          <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
    </article>
  );
}

/** Panel de resumen con selector de dirección */
function CartSummary({ itemCount, total, addresses, loadingAddresses, selectedAddress, onSelectAddress }) {
  const navigate = useNavigate();

  return (
    <aside className={styles.summary} aria-label="Resumen del carrito">
      <h2 className={styles.summaryTitle}>Tu pedido</h2>

      <div className={styles.summaryRow}>
        <span>Productos ({itemCount})</span>
        <span>{formatPrice(total)}</span>
      </div>
      <div className={styles.summaryRow}>
        <span>Envío</span>
        <span>A calcular</span>
      </div>

      <hr className={styles.summaryDivider} />

      <div className={styles.summaryTotal}>
        <span>Total</span>
        <span className={styles.summaryTotalAmount} aria-live="polite">{formatPrice(total)}</span>
      </div>

      {/* Selector de dirección de envío */}
      <div className={styles.addressSection}>
        <div className={styles.addressSectionHeader}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          <span className={styles.addressSectionTitle}>Dirección de envío</span>
        </div>

        {loadingAddresses ? (
          <p className={styles.addressLoading}>Cargando direcciones…</p>
        ) : addresses.length === 0 ? (
          <div className={styles.noAddresses}>
            <p>No tienes direcciones guardadas.</p>
            <Link to="/profile" className={styles.addAddressLink}>+ Agregar dirección</Link>
          </div>
        ) : (
          <div className={styles.addressOptions}>
            {addresses.map(addr => (
              <label
                key={addr.id}
                className={`${styles.addressOption} ${selectedAddress === addr.id ? styles.addressOptionSelected : ''}`}
              >
                <input
                  type="radio"
                  name="shipping-address"
                  value={addr.id}
                  checked={selectedAddress === addr.id}
                  onChange={() => onSelectAddress(addr.id)}
                  className={styles.addressRadio}
                />
                <div className={styles.addressOptionText}>
                  <span className={styles.addressOptionStreet}>{addr.street}</span>
                  <span className={styles.addressOptionDetail}>
                    {addr.city}, {addr.department}
                    {(addr.postalCode || addr.postal_code) ? ` – CP ${addr.postalCode || addr.postal_code}` : ''}
                  </span>
                </div>
              </label>
            ))}
            <Link to="/profile" className={styles.addAddressLink}>+ Agregar otra dirección</Link>
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={() => navigate('/checkout', { state: { addressId: selectedAddress } })}
        className={styles.checkoutButton}
        disabled={itemCount === 0 || (!selectedAddress && addresses.length > 0)}
        aria-disabled={itemCount === 0}
      >
        Proceder al pago →
      </button>

      <Link to="/catalog" className={styles.continueShopping}>← Seguir comprando</Link>
    </aside>
  );
}

/** Página principal del carrito */
export default function CartModule() {
  const { items, loading, error, itemCount, total, updateQuantity, removeItem, refetchCart } = useCart();
  const [addresses, setAddresses] = useState([]);
  const [loadingAddresses, setLoadingAddresses] = useState(true);
  const [selectedAddress, setSelectedAddress] = useState(null);

  useEffect(() => {
    apiClient.get('/api/addresses')
      .then(res => {
        const list = res.data?.data ?? [];
        setAddresses(list);
        if (list.length > 0) setSelectedAddress(list[0].id);
      })
      .catch(() => {})
      .finally(() => setLoadingAddresses(false));
  }, []);

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        <header className={styles.header}>
          <h1 className={styles.title}>Mi carrito</h1>
          {itemCount > 0 && (
            <span className={styles.itemCountBadge} aria-label={`${itemCount} ítems`}>{itemCount}</span>
          )}
        </header>

        {loading && <CartSkeleton />}

        {!loading && error && (
          <div className={styles.errorState} role="alert">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none"
              stroke="var(--color-error)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              aria-hidden="true" className={styles.errorStateIcon}>
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
              <path d="M12 9v4"/><path d="M12 17h.01"/>
            </svg>
            <h2 className={styles.errorStateTitle}>No se pudo cargar el carrito</h2>
            <p className={styles.errorStateText}>{error}</p>
            <button type="button" onClick={refetchCart} className={styles.retryButton}>Intentar nuevamente</button>
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className={styles.emptyState} role="status">
            <div className={styles.emptyStateIconBox} aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/>
                <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>
              </svg>
            </div>
            <h2 className={styles.emptyStateTitle}>Tu carrito está vacío</h2>
            <p className={styles.emptyStateText}>Explora nuestro catálogo y agrega los cafés que más te gusten.</p>
            <Link to="/catalog" className={styles.emptyStateButton}>Ir al catálogo</Link>
          </div>
        )}

        {!loading && !error && items.length > 0 && (
          <div className={styles.cartLayout}>
            <section aria-label="Productos en el carrito">
              <ul className={styles.itemList} role="list">
                {items.map(item => (
                  <li key={item.id} style={{ listStyle: 'none' }}>
                    <CartItem item={item} onUpdateQuantity={updateQuantity} onRemove={removeItem} />
                  </li>
                ))}
              </ul>
            </section>

            <CartSummary
              itemCount={itemCount}
              total={total}
              addresses={addresses}
              loadingAddresses={loadingAddresses}
              selectedAddress={selectedAddress}
              onSelectAddress={setSelectedAddress}
            />
          </div>
        )}
      </div>
    </main>
  );
}
