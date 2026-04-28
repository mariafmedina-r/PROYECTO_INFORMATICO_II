/**
 * components/ProductCard.jsx – Tarjeta de producto para el catálogo.
 *
 * Tarea 12.1 – Requerimientos: 9.3, RNF-001.2
 *
 * Muestra nombre, imagen principal (lazy loading), precio y nombre del Productor.
 * Es un enlace accesible que navega al detalle del producto.
 */

import { Link } from 'react-router-dom';
import { formatPrice } from '../utils/formatPrice';
import styles from '../catalog.module.css';

/** Ícono SVG de taza de café (placeholder de imagen) */
function CoffeeIconSvg() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="40"
      height="40"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
      <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
      <line x1="6" x2="6" y1="2" y2="4" />
      <line x1="10" x2="10" y1="2" y2="4" />
      <line x1="14" x2="14" y1="2" y2="4" />
    </svg>
  );
}

/** Ícono SVG de hoja (productor) */
function LeafIconSvg() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
    </svg>
  );
}

/**
 * @param {Object} props
 * @param {{ id: string, name: string, price: number, producerName: string, producerRegion?: string, mainImageUrl?: string }} props.product
 */
export default function ProductCard({ product }) {
  const { id, name, price, producerName, producerRegion, mainImageUrl } = product;

  return (
    <Link
      to={`/catalog/${id}`}
      className={styles.productCard}
      aria-label={`Ver detalle de ${name}, precio ${formatPrice(price)}`}
    >
      {/* Imagen con lazy loading (RNF-001.2) */}
      <div className={styles.productImageWrapper} aria-hidden="true">
        {mainImageUrl ? (
          <img
            src={mainImageUrl}
            alt={name}
            loading="lazy"
            decoding="async"
            className={styles.productImage}
          />
        ) : (
          <div className={styles.productImagePlaceholder}>
            <span className={styles.productImagePlaceholderIcon}>
              <CoffeeIconSvg />
            </span>
          </div>
        )}
      </div>

      {/* Información del producto */}
      <div className={styles.productCardBody}>
        <h2 className={styles.productName}>{name}</h2>
        <p className={styles.producerName}>
          <span className={styles.producerIcon}>
            <LeafIconSvg />
          </span>
          {producerName}
        </p>
        {producerRegion && (
          <p className={styles.productRegion}>
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
              <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            {producerRegion}
          </p>
        )}
        <p className={styles.productPrice}>{formatPrice(price)}</p>
      </div>
    </Link>
  );
}
