/**
 * OrigenPage.jsx – Página "Origen": El Terroir de los Andes
 *
 * Muestra la historia y diversidad del café colombiano por región.
 */

import styles from './origen.module.css';

const REGIONS = [
  {
    name: 'Huila',
    emoji: '🌋',
    image: '/images/Huila.png',
    tag: 'Volcánico · Tropical',
    description:
      'Suelos volcánicos ricos en minerales y vientos del valle del río Magdalena. Produce tazas balanceadas con notas a caramelo y frutas tropicales dulces.',
    notes: ['Caramelo', 'Frutas tropicales', 'Cuerpo balanceado'],
  },
  {
    name: 'Antioquia',
    emoji: '⛰️',
    image: '/images/Antioquia.png',
    tag: 'Montañoso · Cítrico',
    description:
      'Montañas escarpadas y microclimas ideales. Da como resultado cafés suaves, taza limpia, con una acidez cítrica brillante y cuerpo medio.',
    notes: ['Cítrico brillante', 'Taza limpia', 'Cuerpo medio'],
  },
  {
    name: 'Nariño',
    emoji: '🌊',
    image: '/images/Nariño.png',
    tag: 'Alta altitud · Herbal',
    description:
      'Cultivado a gran altitud bajo la influencia extrema del Pacífico. Desarrolla perfiles únicos, alta acidez cítrica y dulzor herbal marcado.',
    notes: ['Alta acidez', 'Dulzor herbal', 'Perfil único'],
  },
];

export default function OrigenPage() {
  return (
    <main className={styles.page}>
      {/* Hero */}
      <section className={styles.hero} aria-labelledby="origen-title">
        <p className={styles.heroEyebrow}>ESENCIA DEL TERRUÑO ANDINO</p>
      </section>

      {/* Regiones */}
      <section className={styles.regionsSection} aria-labelledby="regions-title">
        <div className={styles.container}>
          <p className={styles.regionsIntro}>
            Conoce algunos de los principales departamentos cafeteros de Colombia y la riqueza de sabores que los hace únicos.
          </p>

          <div className={styles.regionsGrid}>
            {REGIONS.map((region) => (
              <article
                key={region.name}
                className={styles.regionCard}
                style={region.image ? {
                  backgroundImage: `linear-gradient(to bottom, rgba(10,25,15,0.35) 0%, rgba(10,25,15,0.75) 60%, rgba(10,25,15,0.95) 100%), url('${region.image}')`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                } : {}}
              >
                <div className={styles.regionCardTop}>
                  <span className={styles.regionTag}>{region.tag}</span>
                </div>
                <div className={styles.regionCardBody}>
                  <h3 className={`${styles.regionName} ${region.image ? styles.regionNameLight : ''}`}>
                    {region.name}
                  </h3>
                  <p className={`${styles.regionDescription} ${region.image ? styles.regionDescriptionLight : ''}`}>
                    {region.description}
                  </p>
                  <ul className={styles.regionNotes} aria-label="Notas de cata">
                    {region.notes.map((note) => (
                      <li key={note} className={`${styles.regionNote} ${region.image ? styles.regionNoteLight : ''}`}>
                        {note}
                      </li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Llamado a la acción */}
      <section className={styles.ctaSection}>
        <div className={styles.container}>
          <p className={styles.ctaText}>
            Cada taza cuenta una historia de tierra, clima y tradición.
          </p>
          <a href="/catalog" className={styles.ctaButton}>
            Explorar el catálogo
          </a>
        </div>
      </section>
    </main>
  );
}
