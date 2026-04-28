/**
 * components/Breadcrumbs.jsx – Componente de migas de pan reutilizable.
 *
 * Tarea 15 – RNF-008.2
 *
 * Uso:
 *   <Breadcrumbs items={[
 *     { label: 'Inicio', href: '/' },
 *     { label: 'Catálogo', href: '/catalog' },
 *     { label: 'Nombre del producto' },   // último ítem sin href = página actual
 *   ]} />
 *
 * WCAG 2.1 AA:
 *   - <nav aria-label="breadcrumb"> con <ol> semántico
 *   - aria-current="page" en el último ítem
 *   - Navegación completa por teclado (RNF-002.4)
 *   - Área mínima de toque 44×44 px en enlaces (RNF-002.2)
 *   - Contraste adecuado (RNF-002.1)
 *
 * @param {{ items: Array<{ label: string, href?: string }> }} props
 */

import { Link } from 'react-router-dom';
import styles from './Breadcrumbs.module.css';

/**
 * @param {{ items: Array<{ label: string, href?: string }> }} props
 */
export default function Breadcrumbs({ items = [] }) {
  if (!items || items.length === 0) return null;

  return (
    <nav aria-label="breadcrumb" className={styles.breadcrumbs}>
      <ol className={styles.list}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={`${item.label}-${index}`} className={styles.item}>
              {isLast || !item.href ? (
                /* Ítem actual – no es enlace */
                <span
                  className={styles.current}
                  aria-current={isLast ? 'page' : undefined}
                  title={item.label}
                >
                  {item.label}
                </span>
              ) : (
                /* Enlace a página anterior */
                <Link
                  to={item.href}
                  className={styles.link}
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
