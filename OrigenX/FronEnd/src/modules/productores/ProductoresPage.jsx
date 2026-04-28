/**
 * ProductoresPage.jsx – Directorio de productores registrados.
 *
 * Diseño inmersivo con efectos visuales para atraer a los cafeteros.
 */

import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../config/axios';
import { AlertTriangleIcon, CoffeeIcon, LeafIcon, MapPinIcon, SearchIcon } from '../../components/Icons';
import styles from './productores.module.css';
/* ── Partículas aleatorias (granos de café) ─────────────── */

function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

const PARTICLES = Array.from({ length: 15 }, (_, i) => ({
  id: i,
  left:     `${randomBetween(1, 97).toFixed(1)}%`,
  duration: `${randomBetween(6, 11).toFixed(2)}s`,
  delay:    `-${randomBetween(0, 15).toFixed(2)}s`,
  size:     `${randomBetween(6, 13).toFixed(1)}px`,
  height:   `${randomBetween(10, 20).toFixed(1)}px`,
  rise:     `${randomBetween(130, 210).toFixed(0)}px`,
}));

function getInitials(name = '') {
  return name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');
}

const REGION_COLORS = [
  '#1E3D2B', '#417A3D', '#5C3A21', '#1F3A5F',
  '#6B4226', '#2D6A4F', '#40916C', '#1B4332',
];

function getRegionColor(region = '') {
  let hash = 0;
  for (let i = 0; i < region.length; i++) hash = region.charCodeAt(i) + ((hash << 5) - hash);
  return REGION_COLORS[Math.abs(hash) % REGION_COLORS.length];
}

/* ── Tarjeta de productor ───────────────────────────────── */

function ProducerCard({ producer, index }) {
  const cardRef = useRef(null);
  const [visible, setVisible] = useState(false);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  // Intersection Observer para animación de entrada escalonada
  useEffect(() => {
    const el = cardRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Efecto tilt 3D al mover el mouse
  const handleMouseMove = (e) => {
    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientY - rect.top) / rect.height - 0.5) * 14;
    const y = -((e.clientX - rect.left) / rect.width - 0.5) * 14;
    setTilt({ x, y });
  };
  const handleMouseLeave = () => setTilt({ x: 0, y: 0 });

  const accentColor = getRegionColor(producer.region || producer.farmName);
  const initials = getInitials(producer.farmName);
  const producerId = producer.user_id || producer.userId;
  const mainImage = producer.images?.[0] ?? null;

  // Extrae texto plano del HTML de la descripción para el preview
  const descriptionText = producer.description
    ? producer.description.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
    : '';

  return (
    <Link
      to={producerId ? `/producers/${producerId}` : '#'}
      ref={cardRef}
      className={`${styles.card} ${visible ? styles.cardVisible : ''}`}
      style={{
        '--accent': accentColor,
        '--delay': `${index * 80}ms`,
        transform: `perspective(900px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
        transition: tilt.x === 0 && tilt.y === 0
          ? 'transform 0.6s cubic-bezier(0.23,1,0.32,1), opacity 0.6s, translate 0.6s'
          : 'transform 0.1s ease',
        textDecoration: 'none',
        display: 'block',
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      aria-label={`Ver perfil de ${producer.farmName}`}
    >
      {/* Brillo superior */}
      <div className={styles.cardShine} aria-hidden="true" />

      {/* Avatar — imagen real o iniciales */}
      <div className={styles.avatarWrap}>
        <div className={styles.avatarRing} style={{ '--accent': accentColor }} />
        <div className={styles.avatar} style={{ background: accentColor }}>
          {mainImage ? (
            <img
              src={mainImage}
              alt={`Foto de ${producer.farmName}`}
              className={styles.avatarImg}
            />
          ) : (
            <>
              <span className={styles.avatarInitials}>{initials}</span>
              <CoffeeIcon size={18} color="rgba(255,255,255,0.5)" className={styles.avatarEmoji} aria-hidden />
            </>
          )}
        </div>
      </div>

      {/* Contenido */}
      <div className={styles.cardBody}>
        <h3 className={styles.farmName}>{producer.farmName}</h3>

        {producer.region && (
          <span className={styles.regionBadge} style={{ background: accentColor }}>
            <MapPinIcon size={12} color="#fff" style={{ marginRight: 4, flexShrink: 0 }} />
            {producer.region}
          </span>
        )}

        {descriptionText && (
          <p className={styles.description}>
            {descriptionText.length > 120 ? descriptionText.slice(0, 120) + '…' : descriptionText}
          </p>
        )}
      </div>
    </Link>
  );
}

/* ── Página principal ───────────────────────────────────── */

export default function ProductoresPage() {
  const [producers, setProducers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    apiClient.get('/api/producers')
      .then((res) => setProducers(res.data?.data ?? []))
      .catch(() => setError('No se pudieron cargar los productores. Intenta nuevamente.'))
      .finally(() => setLoading(false));
  }, []);

  const filtered = producers.filter((p) => {
    const q = search.toLowerCase();
    return (
      !q ||
      (p.farmName || '').toLowerCase().includes(q) ||
      (p.region || '').toLowerCase().includes(q) ||
      (p.description || '').toLowerCase().includes(q)
    );
  });

  return (
    <main className={styles.page}>
      {/* ── Hero + Buscador ── */}
      <section className={styles.hero} aria-labelledby="prod-title">
        <div className={styles.heroParticles} aria-hidden="true">
          {PARTICLES.map((p) => (
            <span
              key={p.id}
              className={styles.particle}
              style={{
                left:              p.left,
                width:             p.size,
                height:            p.height,
                animationDuration: p.duration,
                animationDelay:    p.delay,
                '--rise':          p.rise,
              }}
            />
          ))}
        </div>
        <div className={styles.heroContent}>
          <p className={styles.heroEyebrow}>ARTESANOS DEL CAFÉ</p>
          <h1 id="prod-title" className={styles.heroTitle}>
            Conoce a Nuestros<br />
            <span className={styles.heroTitleAccent}>Productores</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Cada finca tiene una historia. Cada taza, un rostro detrás.
            Descubre las manos que cultivan el mejor café de Colombia.
          </p>
        </div>
        <div className={styles.heroStats}>
          <div className={styles.heroStat}>
            <span className={styles.heroStatNumber}>{producers.length}</span>
            <span className={styles.heroStatLabel}>Productores</span>
          </div>
          <div className={styles.heroStatDivider} aria-hidden="true" />
          <div className={styles.heroStat}>
            <span className={styles.heroStatNumber}>100%</span>
            <span className={styles.heroStatLabel}>Origen directo</span>
          </div>
          <div className={styles.heroStatDivider} aria-hidden="true" />
          <div className={styles.heroStat}>
            <span className={styles.heroStatNumber}>🇨🇴</span>
            <span className={styles.heroStatLabel}>Colombia</span>
          </div>
        </div>
      </section>

      {/* ── Buscador ── */}
      <div className={styles.searchBar}>
        <div className={styles.container}>
          <div className={styles.searchWrap}>
            <SearchIcon size={18} color="#9ca3af" className={styles.searchIcon} aria-hidden />
            <input
              type="search"
              className={styles.searchInput}
              placeholder="Buscar por finca, región o descripción..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              aria-label="Buscar productores"
            />
            {search && (
              <button
                type="button"
                className={styles.searchClear}
                onClick={() => setSearch('')}
                aria-label="Limpiar búsqueda"
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Grid de productores ── */}
      <section className={styles.gridSection}>
        <div className={styles.container}>
          {loading && (
            <div className={styles.loadingGrid} aria-busy="true" aria-label="Cargando productores">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className={styles.skeleton} />
              ))}
            </div>
          )}

          {error && (
            <div className={styles.errorState} role="alert">
              <AlertTriangleIcon size={40} color="var(--color-error)" className={styles.errorIcon} aria-hidden />
              <p>{error}</p>
              <button
                type="button"
                className={styles.retryBtn}
                onClick={() => window.location.reload()}
              >
                Reintentar
              </button>
            </div>
          )}

          {!loading && !error && filtered.length === 0 && (
            <div className={styles.emptyState}>
              <LeafIcon size={48} color="#9ca3af" className={styles.emptyIcon} aria-hidden />
              <h2 className={styles.emptyTitle}>
                {search ? 'Sin resultados' : 'Aún no hay productores registrados'}
              </h2>
              <p className={styles.emptyText}>
                {search
                  ? `No encontramos productores que coincidan con "${search}".`
                  : 'Pronto los mejores cafeteros de Colombia estarán aquí.'}
              </p>
              {search && (
                <button
                  type="button"
                  className={styles.retryBtn}
                  onClick={() => setSearch('')}
                >
                  Ver todos
                </button>
              )}
            </div>
          )}

          {!loading && !error && filtered.length > 0 && (
            <>
              {search && (
                <p className={styles.resultsCount} aria-live="polite">
                  {filtered.length} productor{filtered.length !== 1 ? 'es' : ''} encontrado{filtered.length !== 1 ? 's' : ''}
                </p>
              )}
              <div className={styles.grid}>
                {filtered.map((producer, i) => (
                  <ProducerCard
                    key={producer.user_id || producer.userId || i}
                    producer={producer}
                    index={i}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      </section>

      {/* ── CTA ── */}
      {!loading && !error && (
        <section className={styles.ctaSection}>
          <div className={styles.container}>
            <div className={styles.ctaCard}>
              <div className={styles.ctaText}>
                <h2 className={styles.ctaTitle}>¿Eres productor de café?</h2>
                <p className={styles.ctaSubtitle}>
                  Únete a nuestra comunidad y conecta directamente con consumidores que valoran tu trabajo.
                </p>
              </div>
              <Link to="/register" className={styles.ctaButton}>
                Registrarme como productor
              </Link>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
