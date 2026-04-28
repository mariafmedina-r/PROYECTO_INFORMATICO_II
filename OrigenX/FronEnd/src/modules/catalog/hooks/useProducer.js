/**
 * hooks/useProducer.js – Hook para obtener el perfil de un productor.
 *
 * Tarea 12.3 – Requerimientos: 4.1, 4.4
 *
 * Llama a GET /api/producers/:id y retorna el perfil, productos del productor,
 * estado de carga y errores.
 */

import { useEffect, useRef, useState } from 'react';
import apiClient from '../../../config/axios';

/**
 * Hook para obtener el perfil de un productor y sus productos activos.
 *
 * @param {string} producerId - ID del productor (Firebase UID).
 * @returns {{ producer, products, loading, error, refetch }}
 */
export function useProducer(producerId) {
  const [producer, setProducer] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const fetchProducer = async () => {
    if (!producerId) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      // Obtener perfil del productor y sus productos en paralelo
      const [profileRes, productsRes] = await Promise.all([
        apiClient.get(`/api/producers/${producerId}`, {
          signal: abortControllerRef.current.signal,
        }),
        apiClient.get('/api/products', {
          params: { producerId: producerId, page_size: 100, includeInactive: false },
          signal: abortControllerRef.current.signal,
        }),
      ]);

      setProducer(profileRes.data?.data ?? profileRes.data);
      setProducts(productsRes.data?.data?.items ?? productsRes.data?.items ?? []);
    } catch (err) {
      if (err.name === 'CanceledError' || err.name === 'AbortError') return;
      if (err.response?.status === 404) {
        setError('Productor no encontrado.');
      } else {
        setError(
          err.response?.data?.error?.message ||
            'No se pudo cargar el perfil del productor. Intenta nuevamente.',
        );
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducer();
    return () => {
      abortControllerRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [producerId]);

  return { producer, products, loading, error, refetch: fetchProducer };
}
