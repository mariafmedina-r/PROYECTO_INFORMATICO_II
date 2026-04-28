/**
 * hooks/useOrderDetail.js – Hook para obtener el detalle de un pedido.
 *
 * Tarea 14.2 – Requerimientos: 15.1, 15.2, 15.3
 *
 * Provee: { order, loading, error, refetch }
 */

import { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../config/axios';

/**
 * Hook para obtener el detalle de un pedido por su ID.
 *
 * @param {string} orderId - ID del pedido.
 * @returns {{ order, loading, error, refetch }}
 */
export function useOrderDetail(orderId) {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOrder = useCallback(async () => {
    if (!orderId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/api/orders/${orderId}`);
      // Backend devuelve { data: { ...pedido } }
      const order = response.data?.data ?? response.data;
      setOrder(order);
    } catch (err) {
      setError(
        err.response?.data?.error?.message ||
          'No se pudo cargar el pedido. Intenta nuevamente.',
      );
    } finally {
      setLoading(false);
    }
  }, [orderId]);

  useEffect(() => {
    fetchOrder();
  }, [fetchOrder]);

  return { order, loading, error, refetch: fetchOrder };
}
