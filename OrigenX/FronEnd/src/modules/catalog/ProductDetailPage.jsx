/**
 * ProductDetailPage.jsx – Página de detalle de un producto.
 *
 * Tarea 12.2 – Requerimientos: 11.1, 11.2, 11.3, RNF-008.2
 * Tarea 13.1 – Requerimientos: 12.1, 12.5
 *
 * Muestra:
 *   - Breadcrumbs (RNF-008.2)
 *   - Galería de imágenes con selección de miniatura
 *   - Nombre, descripción completa, precio, estado de disponibilidad
 *   - Información del Productor con enlace a su perfil (Req. 11.3)
 *   - Mensaje de no disponible si el producto está inactivo (Req. 11.2)
 *   - Botón "Agregar al carrito" (redirige al login si no está autenticado – Req. 12.5)
 *   - Integración real con CartContext para agregar al carrito (Req. 12.1)
 */

import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import { AlertTriangleIcon, CheckCircleIcon, CheckIcon, CoffeeIcon, MapPinIcon, ShoppingCartIcon, XCircleIcon, XIcon } from '../../components/Icons';
import { useProduct } from './hooks/useProduct';
import { formatPrice } from './utils/formatPrice';
import styles from './catalog.module.css';

/** Skeleton de carga para el detalle */
function DetailSkeleton() {
  return (
    <div
      className={styles.detailGrid}
      aria-busy="true"
      aria-label="Cargando detalle del producto"
    >
      {/* Imagen */}
      <div>
        <div
          style={{ width: '100%', paddingTop: '75%', borderRadius: '0.75rem' }}
          className={styles.skeletonImage}
          aria-hidden="true"
        />
      </div>
      {/* Info */}
      <div className={styles.skeletonBody} style={{ gap: '1rem' }}>
        <div className={styles.skeletonLine} style={{ width: '30%', height: '1.5rem' }} />
        <div className={styles.skeletonLine} style={{ width: '80%', height: '2rem' }} />
        <div className={styles.skeletonLine} style={{ width: '40%', height: '1.75rem' }} />
        <div className={styles.skeletonLine} />
        <div className={styles.skeletonLine} />
        <div className={`${styles.skeletonLine} ${styles.skeletonLineShort}`} />
      </div>
    </div>
  );
}

export default function ProductDetailPage() {
  const { productId } = useParams();
  const { isAuthenticated, isConsumer } = useAuth();
  const { addItem } = useCart();
  const navigate = useNavigate();
  const { product, loading, error, refetch } = useProduct(productId);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [addingToCart, setAddingToCart] = useState(false);
  const [cartFeedback, setCartFeedback] = useState(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  const isActive = product?.status === 'active';
  const images = product?.images ?? [];
  const selectedImage = images[selectedImageIndex];
  const stock = product?.stock ?? 0;
  const [quantity, setQuantity] = useState(1);

  const maxQty = stock > 0 ? stock : 1;
  const safeQty = Math.min(quantity, maxQty);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/catalog/${productId}` } } });
      return;
    }

    if (!isConsumer) {
      setCartFeedback({ type: 'error', message: 'Solo los consumidores pueden agregar productos al carrito.' });
      return;
    }

    setAddingToCart(true);
    setCartFeedback(null);

    const result = await addItem(product.id, safeQty);

    setAddingToCart(false);

    if (result.success) {
      setCartFeedback({ type: 'success', message: '¡Producto agregado al carrito!' });
      // Limpiar el feedback después de 3 segundos
      setTimeout(() => setCartFeedback(null), 3000);
    } else {
      setCartFeedback({ type: 'error', message: result.error });
    }
  };

  return (
    <main className={styles.detailPage}>
      <div className={styles.detailContainer}>
        {/* Breadcrumbs (RNF-008.2) */}
        <nav aria-label="Ruta de navegación" className={styles.breadcrumbs}>
          <ol className={styles.breadcrumbList}>
            <li className={styles.breadcrumbItem}>
              <Link to="/catalog" className={styles.breadcrumbLink}>
                Catálogo
              </Link>
            </li>
            <li className={styles.breadcrumbItem}>
              <span className={styles.breadcrumbCurrent} aria-current="page">
                {loading ? 'Cargando…' : (product?.name ?? 'Producto')}
              </span>
            </li>
          </ol>
        </nav>

        {/* Estado de carga */}
        {loading && <DetailSkeleton />}

        {/* Estado de error */}
        {!loading && error && (
          <div className={styles.errorState} role="alert">
            <AlertTriangleIcon size={40} color="var(--color-error)" aria-hidden className={styles.errorStateIcon} />
            <h1 className={styles.errorStateTitle}>No se pudo cargar el producto</h1>
            <p className={styles.errorStateText}>{error}</p>
            <button type="button" onClick={refetch} className={styles.retryButton}>
              Intentar nuevamente
            </button>
          </div>
        )}

        {/* Detalle del producto */}
        {!loading && !error && product && (
          <div className={styles.detailGrid}>
            {/* Galería de imágenes */}
            <section aria-label="Galería de imágenes del producto">
              <div className={styles.galleryWrapper}>
                {/* Imagen principal */}
                <div className={styles.mainImageWrapper}>
                  {selectedImage ? (
                    <button
                      type="button"
                      onClick={() => setLightboxOpen(true)}
                      className={styles.mainImageButton}
                      aria-label="Ampliar imagen"
                      title="Haz clic para ampliar"
                    >
                      <img
                        src={selectedImage.url}
                        alt={`${product.name} – imagen ${selectedImageIndex + 1} de ${images.length}`}
                        loading="eager"
                        decoding="async"
                        className={styles.mainImage}
                      />
                      <span className={styles.mainImageZoomHint} aria-hidden="true">🔍</span>
                    </button>
                  ) : (
                    <div className={styles.mainImagePlaceholder} aria-label="Sin imagen disponible">
                      <CoffeeIcon size={48} color="#9ca3af" aria-hidden className={styles.mainImagePlaceholderIcon} />
                      <span>Sin imagen</span>
                    </div>
                  )}
                </div>

                {/* Miniaturas */}
                {images.length > 1 && (
                  <div
                    className={styles.thumbnailList}
                    role="list"
                    aria-label="Miniaturas de imágenes"
                  >
                    {images.map((img, index) => (
                      <button
                        key={img.id ?? index}
                        type="button"
                        role="listitem"
                        onClick={() => setSelectedImageIndex(index)}
                        className={`${styles.thumbnailButton} ${
                          index === selectedImageIndex ? styles.thumbnailButtonActive : ''
                        }`}
                        aria-label={`Ver imagen ${index + 1}`}
                        aria-pressed={index === selectedImageIndex}
                      >
                        <img
                          src={img.url}
                          alt=""
                          loading="lazy"
                          decoding="async"
                          className={styles.thumbnailImage}
                        />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </section>

            {/* Información del producto */}
            <section aria-label="Información del producto" className={styles.detailInfo}>
              {/* Badge de estado + unidades */}
              <div className={styles.detailBadgeRow}>
                <span
                  className={`${styles.detailBadge} ${
                    isActive ? styles.badgeActive : styles.badgeInactive
                  }`}
                  aria-label={`Estado: ${isActive ? 'Disponible' : 'No disponible'}`}
                >
                  {isActive
                    ? <><CheckIcon size={14} style={{ marginRight: 4 }} /> Disponible</>
                    : <><XIcon size={14} style={{ marginRight: 4 }} /> No disponible</>
                  }
                </span>
                {/* Unidades al lado derecho del badge */}
                {isActive && (
                  <span className={stock > 0 ? styles.detailStockAvailable : styles.detailStockEmpty}>
                    {stock > 0
                      ? `${stock} ${stock === 1 ? 'unidad' : 'unidades'}`
                      : 'Sin stock'}
                  </span>
                )}
              </div>

              {/* Nombre */}
              <h1 className={styles.detailProductName}>{product.name}</h1>

              {/* Precio */}
              <p className={styles.detailPrice} aria-label={`Precio: ${formatPrice(product.price)}`}>
                {formatPrice(product.price)}
              </p>

              {/* Mensaje de no disponible (Req. 11.2) */}
              {!isActive && (
                <div className={styles.unavailableBanner} role="alert">
                  Este producto no está disponible actualmente. Puede que el productor
                  lo haya desactivado temporalmente.
                </div>
              )}

              {/* Descripción */}
              <div>
                <h2 className={styles.detailSectionTitle}>Descripción</h2>
                <div
                  className={styles.detailDescription}
                  dangerouslySetInnerHTML={{ __html: product.description }}
                />
              </div>

              {/* Información del Productor (Req. 11.3) */}
              {product.producerId && (
                <div>
                  <h2 className={styles.detailSectionTitle}>Productor</h2>
                  <div className={styles.producerCard}>
                    <p className={styles.producerCardName}>
                      {product.producerName ?? 'Productor'}
                    </p>
                    {product.producerRegion && (
                      <p className={styles.producerCardRegion}>
                        <MapPinIcon size={14} style={{ marginRight: 4, flexShrink: 0 }} />
                        {product.producerRegion}
                      </p>
                    )}
                    <Link
                      to={`/producers/${product.producerId}`}
                      className={styles.producerCardLink}
                    >
                      Ver perfil del productor →
                    </Link>
                  </div>
                </div>
              )}

              {/* Selector de cantidad — solo si activo y con stock */}
              {isActive && stock > 0 && (
                <div className={styles.quantityRow}>
                  <label htmlFor="qty-input" className={styles.quantityLabel}>
                    Cantidad
                  </label>
                  <div className={styles.quantityControl}>
                    <button
                      type="button"
                      className={styles.quantityBtn}
                      onClick={() => setQuantity(q => Math.max(1, q - 1))}
                      disabled={safeQty <= 1}
                      aria-label="Reducir cantidad"
                    >
                      −
                    </button>
                    <input
                      id="qty-input"
                      type="number"
                      min={1}
                      max={maxQty}
                      value={safeQty}
                      onChange={e => {
                        const v = parseInt(e.target.value, 10);
                        if (!isNaN(v)) setQuantity(Math.min(Math.max(1, v), maxQty));
                      }}
                      className={styles.quantityInput}
                      aria-label="Cantidad a agregar al carrito"
                    />
                    <button
                      type="button"
                      className={styles.quantityBtn}
                      onClick={() => setQuantity(q => Math.min(maxQty, q + 1))}
                      disabled={safeQty >= maxQty}
                      aria-label="Aumentar cantidad"
                    >
                      +
                    </button>
                  </div>
                </div>
              )}

              {/* Aviso para productores */}
              {isAuthenticated && !isConsumer && (
                <div className={styles.unavailableBanner} role="note">
                  Los productores no pueden realizar compras. Usa una cuenta de consumidor para agregar productos al carrito.
                </div>
              )}

              {/* Botón agregar al carrito */}
              <button
                type="button"
                onClick={handleAddToCart}
                disabled={!isActive || stock === 0 || addingToCart || (isAuthenticated && !isConsumer)}
                className={styles.addToCartButton}
                aria-disabled={!isActive || stock === 0 || addingToCart || (isAuthenticated && !isConsumer)}
                aria-busy={addingToCart}
              >
                {addingToCart
                  ? 'Agregando…'
                  : isActive && stock > 0
                  ? <><ShoppingCartIcon size={18} style={{ marginRight: 6 }} /> Agregar al carrito</>
                  : isActive && stock === 0
                  ? 'Sin stock'
                  : 'Producto no disponible'}
              </button>

              {/* Feedback de agregar al carrito */}
              {cartFeedback && (
                <div
                  role="status"
                  aria-live="polite"
                  style={{
                    padding: '0.75rem 1rem',
                    borderRadius: '0.5rem',
                    fontSize: '1rem',
                    backgroundColor: cartFeedback.type === 'success' ? '#dcfce7' : '#fef2f2',
                    color: cartFeedback.type === 'success' ? '#166534' : '#dc2626',
                    border: `1px solid ${cartFeedback.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
                  }}
                >
                  {cartFeedback.type === 'success'
                    ? <><CheckIcon size={16} style={{ marginRight: 4 }} /> {cartFeedback.message}</>
                    : <><XIcon size={16} style={{ marginRight: 4 }} /> {cartFeedback.message}</>
                  }
                </div>
              )}
            </section>
          </div>
        )}
      </div>

      {/* Lightbox de imagen ampliada */}
      {lightboxOpen && images.length > 0 && (
        <div
          className={styles.lightboxOverlay}
          role="dialog"
          aria-modal="true"
          aria-label="Vista ampliada de imagen"
          onClick={(e) => { if (e.target === e.currentTarget) setLightboxOpen(false); }}
          onKeyDown={(e) => {
            if (e.key === 'Escape') setLightboxOpen(false);
            if (e.key === 'ArrowRight') setSelectedImageIndex(i => (i + 1) % images.length);
            if (e.key === 'ArrowLeft') setSelectedImageIndex(i => (i - 1 + images.length) % images.length);
          }}
          tabIndex={-1}
          // eslint-disable-next-line jsx-a11y/no-autofocus
          ref={el => el?.focus()}
        >
          {/* Botón cerrar */}
          <button
            type="button"
            className={styles.lightboxClose}
            onClick={() => setLightboxOpen(false)}
            aria-label="Cerrar vista ampliada"
          >
            <XIcon size={20} />
          </button>

          <div className={styles.lightboxContent}>
            {/* Flecha anterior */}
            {images.length > 1 && (
              <button
                type="button"
                className={`${styles.lightboxNav} ${styles.lightboxPrev}`}
                onClick={() => setSelectedImageIndex(i => (i - 1 + images.length) % images.length)}
                aria-label="Imagen anterior"
              >
                ‹
              </button>
            )}

            {/* Imagen ampliada */}
            <img
              src={images[selectedImageIndex].url}
              alt={`${product.name} – imagen ${selectedImageIndex + 1} de ${images.length}`}
              className={styles.lightboxImg}
            />

            {/* Flecha siguiente */}
            {images.length > 1 && (
              <button
                type="button"
                className={`${styles.lightboxNav} ${styles.lightboxNext}`}
                onClick={() => setSelectedImageIndex(i => (i + 1) % images.length)}
                aria-label="Imagen siguiente"
              >
                ›
              </button>
            )}

            {/* Indicadores de puntos */}
            {images.length > 1 && (
              <div className={styles.lightboxDots} role="tablist" aria-label="Seleccionar imagen">
                {images.map((_, idx) => (
                  <button
                    key={idx}
                    type="button"
                    role="tab"
                    aria-selected={idx === selectedImageIndex}
                    aria-label={`Imagen ${idx + 1}`}
                    className={`${styles.lightboxDot} ${idx === selectedImageIndex ? styles.lightboxDotActive : ''}`}
                    onClick={() => setSelectedImageIndex(idx)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
