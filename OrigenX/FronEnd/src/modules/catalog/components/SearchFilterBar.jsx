/**
 * components/SearchFilterBar.jsx – Barra de búsqueda y filtros del catálogo.
 *
 * - Todos los filtros en una sola línea.
 * - Texto: búsqueda automática con debounce (sin botón Buscar).
 * - Precio: se aplica al perder el foco (onBlur) o al presionar Enter.
 * - Departamento: se aplica al instante (select).
 */

import { useEffect, useRef, useState } from 'react';
import styles from '../catalog.module.css';

const COFFEE_REGIONS = [
  'Caldas',
  'Quindío',
  'Risaralda',
  'Antioquia',
  'Tolima',
  'Huila',
  'Valle del Cauca',
  'Cauca',
  'Nariño',
];

const DEBOUNCE_MS = 400;

export default function SearchFilterBar({ filters, onFiltersChange }) {
  const [localQ,        setLocalQ]        = useState(filters.q);
  const [localMinPrice, setLocalMinPrice] = useState(filters.minPrice);
  const [localMaxPrice, setLocalMaxPrice] = useState(filters.maxPrice);
  const debounceRef = useRef(null);

  // Sincronizar si los filtros se limpian externamente
  useEffect(() => { setLocalQ(filters.q);               }, [filters.q]);
  useEffect(() => { setLocalMinPrice(filters.minPrice); }, [filters.minPrice]);
  useEffect(() => { setLocalMaxPrice(filters.maxPrice); }, [filters.maxPrice]);

  // Texto: debounce automático
  const handleQChange = (e) => {
    const val = e.target.value;
    setLocalQ(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      onFiltersChange({ ...filters, q: val });
    }, DEBOUNCE_MS);
  };

  // Precio: solo actualiza estado local mientras escribe
  const handleMinPriceChange = (e) => setLocalMinPrice(e.target.value);
  const handleMaxPriceChange = (e) => setLocalMaxPrice(e.target.value);

  // Precio: aplica al perder foco
  const applyPrice = () => {
    onFiltersChange({ ...filters, minPrice: localMinPrice, maxPrice: localMaxPrice });
  };

  // Precio: aplica al presionar Enter
  const handlePriceKeyDown = (e) => {
    if (e.key === 'Enter') applyPrice();
  };

  // Departamento: aplica al instante
  const handleRegionChange = (e) => {
    onFiltersChange({ ...filters, region: e.target.value });
  };

  const hasActiveFilters =
    filters.q || filters.minPrice || filters.maxPrice || filters.region;

  const handleClearFilters = () => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    setLocalQ('');
    setLocalMinPrice('');
    setLocalMaxPrice('');
    onFiltersChange({ q: '', minPrice: '', maxPrice: '', region: '' });
  };

  return (
    <div className={styles.searchFilterBar} role="search" aria-label="Buscar y filtrar productos">
      <div className={styles.filterRowSingle}>

        {/* Búsqueda por texto */}
        <div className={styles.filterGroupFlex}>
          <label htmlFor="catalog-search" className={styles.filterLabel}>
            Buscar
          </label>
          <input
            id="catalog-search"
            type="search"
            value={localQ}
            onChange={handleQChange}
            placeholder="Producto o finca…"
            className={styles.filterInput}
            aria-label="Buscar por nombre de producto o finca"
            autoComplete="off"
          />
        </div>

        {/* Precio mínimo */}
        <div className={styles.filterGroupFixed}>
          <label htmlFor="filter-min-price" className={styles.filterLabel}>
            Precio mín.
          </label>
          <input
            id="filter-min-price"
            type="number"
            min="0"
            step="1000"
            value={localMinPrice}
            onChange={handleMinPriceChange}
            onBlur={applyPrice}
            onKeyDown={handlePriceKeyDown}
            placeholder="0"
            className={styles.filterInput}
            aria-label="Precio mínimo en pesos colombianos"
          />
        </div>

        {/* Precio máximo */}
        <div className={styles.filterGroupFixed}>
          <label htmlFor="filter-max-price" className={styles.filterLabel}>
            Precio máx.
          </label>
          <input
            id="filter-max-price"
            type="number"
            min="0"
            step="1000"
            value={localMaxPrice}
            onChange={handleMaxPriceChange}
            onBlur={applyPrice}
            onKeyDown={handlePriceKeyDown}
            placeholder="Sin límite"
            className={styles.filterInput}
            aria-label="Precio máximo en pesos colombianos"
          />
        </div>

        {/* Departamento */}
        <div className={styles.filterGroupFixed}>
          <label htmlFor="filter-region" className={styles.filterLabel}>
            Departamento
          </label>
          <select
            id="filter-region"
            value={filters.region}
            onChange={handleRegionChange}
            className={styles.filterSelect}
            aria-label="Filtrar por departamento cafetero"
          >
            <option value="">Todos</option>
            {COFFEE_REGIONS.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        {/* Limpiar filtros */}
        {hasActiveFilters && (
          <div className={styles.filterGroupAuto}>
            <label className={styles.filterLabel}>&nbsp;</label>
            <button
              type="button"
              onClick={handleClearFilters}
              className={styles.clearFiltersButton}
              aria-label="Limpiar todos los filtros"
            >
              Limpiar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
