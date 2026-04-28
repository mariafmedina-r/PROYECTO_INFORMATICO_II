/**
 * ProducerProfilePage.jsx – Página de perfil público de un productor.
 */

import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useProducer } from './hooks/useProducer';
import ProductCard from './components/ProductCard';
import styles from './catalog.module.css';

/** Skeleton de carga */
function ProfileSkeleton() {
  return (
    <div className={styles.profileSkeleton}>
      <div className={styles.profileSkeletonHero} />
      <div className={styles.profileContainer}>
        <div className={styles.profileSkeletonBody}>
          {[1,2,3].map(i => <div key={i} className={styles.skeletonLine} style={{ width: `${70 - i*15}%`, height: '1rem', marginBottom: '0.75rem' }} />)}
        </div>
      </div>
    </div>
  );
}

/** Lightbox simple */
function Lightbox({ images, index, onClose }) {
  const [current, setCurrent] = useState(index);
  const prev = () => setCurrent(c => (c - 1 + images.length) % images.length);
  const next = () => setCurrent(c => (c + 1) % images.length);

  return (
    <div className={styles.lightboxOverlay} onClick={onClose} role="dialog" aria-modal="true" aria-label="Galería de imágenes">
      <button className={styles.lightboxClose} onClick={onClose} aria-label="Cerrar">✕</button>
      <div className={styles.lightboxContent} onClick={e => e.stopPropagation()}>
        <img src={images[current]} alt={`Imagen ${current + 1}`} className={styles.lightboxImg} />
        {images.length > 1 && (
          <>
            <button className={`${styles.lightboxNav} ${styles.lightboxPrev}`} onClick={prev} aria-label="Anterior">‹</button>
            <button className={`${styles.lightboxNav} ${styles.lightboxNext}`} onClick={next} aria-label="Siguiente">›</button>
            <div className={styles.lightboxDots}>
              {images.map((_, i) => (
                <button key={i} className={`${styles.lightboxDot} ${i === current ? styles.lightboxDotActive : ''}`}
                  onClick={() => setCurrent(i)} aria-label={`Imagen ${i + 1}`} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function ProducerProfilePage() {
  const { producerId } = useParams();
  const { producer, products, loading, error, refetch } = useProducer(producerId);
  const [lightboxIndex, setLightboxIndex] = useState(null);

  const mainImage   = producer?.images?.[0] ?? null;
  const extraImages = producer?.images?.slice(1) ?? [];
  const avatarLetter = producer?.farmName?.[0]?.toUpperCase() ?? '☕';

  const emailContact  = producer?.showAltEmail && producer?.altEmail
    ? producer.altEmail
    : (producer?.showRegisterEmail && producer?.email ? producer.email : null);
  const whatsappNum   = producer?.whatsapp?.replace(/\D/g, '') ?? null;
  const whatsappMsg   = encodeURIComponent('Hola, vi tu perfil en Conexión Cafetera y me interesa tu café');

  if (loading) return <ProfileSkeleton />;

  if (error) return (
    <main className={styles.profilePage}>
      <div className={styles.profileContainer}>
        <div className={styles.errorState} role="alert">
          <span className={styles.errorStateIcon}>⚠️</span>
          <h1 className={styles.errorStateTitle}>No se pudo cargar el perfil</h1>
          <p className={styles.errorStateText}>{error}</p>
          <button type="button" onClick={refetch} className={styles.retryButton}>Intentar nuevamente</button>
        </div>
      </div>
    </main>
  );

  if (!producer) return null;

  const allImages = producer.images ?? [];

  return (
    <main className={styles.profilePage}>

      {/* ── Hero ─────────────────────────────────────────── */}
      <div className={styles.profileHero} style={mainImage ? { backgroundImage: `url(${mainImage})` } : {}}>
        <div className={styles.profileHeroOverlay} />
        <div className={styles.profileHeroContent}>
          {/* Breadcrumb */}
          <nav aria-label="Ruta de navegación" className={styles.profileBreadcrumb}>
            <Link to="/productores" className={styles.profileBreadcrumbLink}>Productores</Link>
            <span aria-hidden="true">/</span>
            <span>{producer.farmName}</span>
          </nav>

          {/* Avatar + nombre */}
          <div className={styles.profileHeroMeta}>
            <div className={styles.profileAvatarLg}>
              {mainImage
                ? <img src={mainImage} alt={producer.farmName} className={styles.profileAvatarImg} />
                : <span>{avatarLetter}</span>}
            </div>
            <div>
              <h1 className={styles.profileHeroName}>{producer.farmName}</h1>
              {producer.region && (
                <span className={styles.profileHeroRegion}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
                    <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                  {producer.region}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Cuerpo ───────────────────────────────────────── */}
      <div className={styles.profileContainer}>
        <div className={styles.profileBody}>

          {/* Columna principal */}
          <div className={styles.profileMain}>

            {/* Descripción */}
            {producer.description && (
              <section className={styles.profileSection}>
                <h2 className={styles.profileSectionHeading}>Sobre la finca</h2>
                <div
                  className={styles.profileRichText}
                  dangerouslySetInnerHTML={{ __html: producer.description }}
                />
              </section>
            )}

            {/* Galería */}
            {allImages.length > 0 && (
              <section className={styles.profileSection}>
                <h2 className={styles.profileSectionHeading}>Galería</h2>
                <div className={styles.profileGalleryGrid}>
                  {allImages.map((url, i) => (
                    <button
                      key={i}
                      className={`${styles.profileGalleryThumb} ${i === 0 ? styles.profileGalleryThumbMain : ''}`}
                      onClick={() => setLightboxIndex(i)}
                      aria-label={`Ver imagen ${i + 1}`}
                    >
                      <img src={url} alt={`${producer.farmName} – ${i + 1}`} className={styles.profileGalleryImg} />
                      {i === 3 && allImages.length > 4 && (
                        <div className={styles.profileGalleryMore}>+{allImages.length - 4}</div>
                      )}
                    </button>
                  )).slice(0, 4)}
                </div>
              </section>
            )}

            {/* Productos */}
            <section className={styles.profileSection}>
              <h2 className={styles.profileSectionHeading}>
                Productos disponibles
                {products.length > 0 && <span className={styles.profileSectionCount}>{products.length}</span>}
              </h2>
              {products.length === 0 ? (
                <div className={styles.emptyState} role="status">
                  <span className={styles.emptyStateIcon}>☕</span>
                  <p className={styles.emptyStateText}>Este productor no tiene productos activos en este momento.</p>
                </div>
              ) : (
                <div className={styles.productGrid}>
                  {products.map(p => <ProductCard key={p.id} product={p} />)}
                </div>
              )}
            </section>
          </div>

          {/* Sidebar de contacto */}
          <aside className={styles.profileSidebar}>
            <div className={styles.profileContactCard}>
              <h3 className={styles.profileContactTitle}>Contacto</h3>
              {producer.region && (
                <div className={styles.profileContactRow}>
                  <span className={styles.profileContactIcon}>
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/>
                      <circle cx="12" cy="10" r="3"/>
                    </svg>
                  </span>
                  <span>{producer.region}</span>
                </div>
              )}
              {producer.showRegisterEmail && producer.email && (
                <div className={styles.profileContactRow}>
                  <span className={styles.profileContactIcon}>
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <rect x="2" y="4" width="20" height="16" rx="2"/>
                      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                    </svg>
                  </span>
                  <a href={`mailto:${producer.email}`} className={styles.profileContactLink}>{producer.email}</a>
                </div>
              )}
              {producer.showAltEmail && producer.altEmail && (
                <div className={styles.profileContactRow}>
                  <span className={styles.profileContactIcon}>
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <rect x="2" y="4" width="20" height="16" rx="2"/>
                      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                    </svg>
                  </span>
                  <a href={`mailto:${producer.altEmail}`} className={styles.profileContactLink}>{producer.altEmail}</a>
                </div>
              )}
              {producer.whatsapp && (
                <div className={styles.profileContactRow}>
                  <span className={`${styles.profileContactIcon} ${styles.profileContactIconWa}`}>
                    <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/>
                    </svg>
                  </span>
                  <a
                    href={`https://wa.me/${producer.whatsapp.replace(/\D/g, '')}?text=Hola,%20vi%20tu%20perfil%20en%20Conexi%C3%B3n%20Cafetera%20y%20me%20interesa%20tu%20caf%C3%A9`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`${styles.profileContactLink} ${styles.profileContactLinkWa}`}
                  >
                    {producer.whatsapp}
                  </a>
                </div>
              )}
            </div>
          </aside>
        </div>
      </div>

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <Lightbox images={allImages} index={lightboxIndex} onClose={() => setLightboxIndex(null)} />
      )}

      {/* Botones flotantes de contacto — solo móvil */}
      {(emailContact || whatsappNum) && (
        <div
          className={styles.floatingContact}
          aria-label="Contactar al productor"
        >
          {emailContact && (
            <a
              href={`mailto:${emailContact}`}
              className={styles.floatingContactBtn}
              aria-label={`Enviar correo a ${emailContact}`}
              title={emailContact}
            >
              {/* Ícono email */}
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
              </svg>
            </a>
          )}
          {whatsappNum && (
            <a
              href={`https://wa.me/${whatsappNum}?text=${whatsappMsg}`}
              target="_blank"
              rel="noopener noreferrer"
              className={`${styles.floatingContactBtn} ${styles.floatingContactBtnWa}`}
              aria-label="Contactar por WhatsApp"
              title="WhatsApp"
            >
              {/* Ícono WhatsApp */}
              <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/>
              </svg>
            </a>
          )}
        </div>
      )}
    </main>
  );
}
