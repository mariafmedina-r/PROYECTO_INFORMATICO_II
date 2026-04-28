/**
 * hooks/useCatalog.js – Hook para obtener el catálogo de productos con paginación y filtros.
 *
 * Tarea 12.1 – Requerimientos: 9.1, 9.4, 10.1, 10.2, 10.3, 10.5
 *
 * Llama a GET /api/products con los parámetros de búsqueda y paginación.
 * Retorna los productos, el estado de carga, errores y metadatos de paginación.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import apiClient from '../../../config/axios';

const PAGE_SIZE = 20;

/**
 * @typedef {Object} CatalogFilters
 * @property {string} q - Término de búsqueda por texto.
 * @property {string} minPrice - Precio mínimo.
 * @property {string} maxPrice - Precio máximo.
 * @property {string} region - Región del productor.
 */

/**
 * Hook para obtener el catálogo paginado con filtros.
 *
 * @param {CatalogFilters} filters - Filtros activos.
 * @param {number} page - Página actual (1-indexed).
 * @returns {{ products, totalPages, totalItems, loading, error, refetch }}
 */
export function useCatalog(filters, page) {
  const [products, setProducts] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Ref para cancelar peticiones obsoletas
  const abortControllerRef = useRef(null);

  const fetchProducts = useCallback(async () => {
    // Cancelar petición anterior si existe
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const params = {
        page,
        page_size: PAGE_SIZE,
      };

      if (filters.q?.trim()) params.q = filters.q.trim();
      if (filters.minPrice !== '' && filters.minPrice !== null && filters.minPrice !== undefined) params.min_price = filters.minPrice;
      if (filters.maxPrice !== '' && filters.maxPrice !== null && filters.maxPrice !== undefined) params.max_price = filters.maxPrice;
      if (filters.region?.trim()) params.region = filters.region.trim();

      const response = await apiClient.get('/api/products', {
        params,
        signal: abortControllerRef.current.signal,
      });

      const data = response.data?.data ?? response.data;
      setProducts(data.items ?? []);
      setTotalItems(data.total ?? 0);
      setTotalPages(Math.ceil((data.total ?? 0) / PAGE_SIZE) || 1);
    } catch (err) {
      if (err.name === 'CanceledError' || err.name === 'AbortError') return;
      setError(
        err.response?.data?.error?.message ||
          'No se pudo cargar el catálogo. Intenta nuevamente.',
      );
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchProducts();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchProducts]);

  return { products, totalPages, totalItems, loading, error, refetch: fetchProducts };
}
