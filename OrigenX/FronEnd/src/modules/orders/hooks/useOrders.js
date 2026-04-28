/**
 * hooks/useOrders.js – Hook para obtener el historial de pedidos del consumidor.
 *
 * Tarea 14.2 – Requerimientos: 15.1, 15.2, 15.3
 *
 * Provee: { orders, loading, error, refetch }
 */

import { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../config/axios';

/**
 * Hook para obtener los pedidos del consumidor autenticado.
 * Los pedidos se ordenan por fecha descendente.
 *
 * @returns {{ orders, loading, error, refetch }}
 */
export function useOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/orders');
      // Backend devuelve { data: [...] }
      const raw = response.data?.data ?? response.data?.orders ?? response.data ?? [];
      const data = Array.isArray(raw) ? raw : [];
      // Ordenar por fecha descendente
      const sorted = [...data].sort((a, b) => {
        const dateA = new Date(a.createdAt ?? a.created_at ?? 0);
        const dateB = new Date(b.createdAt ?? b.created_at ?? 0);
        return dateB - dateA;
      });
      setOrders(sorted);
    } catch (err) {
      setError(
        err.response?.data?.error?.message ||
          'No se pudieron cargar los pedidos. Intenta nuevamente.',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return { orders, loading, error, refetch: fetchOrders };
}
