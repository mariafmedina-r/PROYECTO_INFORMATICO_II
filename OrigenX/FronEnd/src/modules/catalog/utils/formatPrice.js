/**
 * utils/formatPrice.js – Utilidad para formatear precios en pesos colombianos.
 */

/**
 * Formatea un número como precio en COP.
 *
 * @param {number} price - Precio a formatear.
 * @returns {string} Precio formateado (ej. "$ 45.000").
 */
export function formatPrice(price) {
  if (price == null || isNaN(price)) return '—';
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}
