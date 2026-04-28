/**
 * hooks/useProduct.js – Hook para obtener el detalle de un producto.
 *
 * Tarea 12.2 – Requerimientos: 11.1, 11.2, 11.3
 *
 * Llama a GET /api/products/:id y retorna el producto, estado de carga y errores.
 */

import { useEffect, useRef, useState } from 'react';
import apiClient from '../../../config/axios';

/**
 * Hook para obtener el detalle de un producto por su ID.
 *
 * @param {string} productId - ID del producto.
 * @returns {{ product, loading, error, refetch }}
 */
export function useProduct(productId) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const fetchProduct = async () => {
    if (!productId) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(`/api/products/${productId}`, {
        signal: abortControllerRef.current.signal,
      });

      // El backend retorna { data: { ...producto }, message?: string }
      const payload = response.data?.data ?? response.data;
      // Aplanar producerRegion desde el objeto producer anidado
      const product = {
        ...payload,
        producerRegion: payload.producer?.region ?? payload.producerRegion ?? null,
      };
      setProduct(product);
    } catch (err) {
      if (err.name === 'CanceledError' || err.name === 'AbortError') return;
      if (err.response?.status === 404) {
        setError('Producto no encontrado.');
      } else {
        setError(
          err.response?.data?.error?.message ||
            'No se pudo cargar el producto. Intenta nuevamente.',
        );
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProduct();
    return () => {
      abortControllerRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productId]);

  return { product, loading, error, refetch: fetchProduct };
}
