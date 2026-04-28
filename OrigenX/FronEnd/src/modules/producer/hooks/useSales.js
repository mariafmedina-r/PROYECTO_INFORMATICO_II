/**
 * hooks/useSales.js – Hook para obtener datos de ventas del productor.
 *
 * Tarea 14.1 – Requerimientos: 16.1, 16.2, 16.3
 *
 * Provee: { sales, monthlySummary, loading, error, filterByDateRange }
 */

import { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../config/axios';

/**
 * Calcula el resumen mensual (mes actual y mes anterior) a partir de la lista de ventas.
 *
 * @param {Array} sales
 * @returns {{ currentMonth: number, previousMonth: number }}
 */
function computeMonthlySummary(sales) {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth(); // 0-indexed

  let currentMonthTotal = 0;
  let previousMonthTotal = 0;

  for (const sale of sales) {
    const date = new Date(sale.createdAt || sale.created_at);
    if (isNaN(date.getTime())) continue;

    const saleYear = date.getFullYear();
    const saleMonth = date.getMonth();

    if (saleYear === currentYear && saleMonth === currentMonth) {
      currentMonthTotal += sale.total ?? 0;
    } else {
      // Mes anterior
      const prevMonth = currentMonth === 0 ? 11 : currentMonth - 1;
      const prevYear = currentMonth === 0 ? currentYear - 1 : currentYear;
      if (saleYear === prevYear && saleMonth === prevMonth) {
        previousMonthTotal += sale.total ?? 0;
      }
    }
  }

  return { currentMonth: currentMonthTotal, previousMonth: previousMonthTotal };
}

/**
 * Hook para obtener y filtrar las ventas del productor autenticado.
 *
 * @returns {{ sales, monthlySummary, loading, error, filterByDateRange }}
 */
export function useSales() {
  const [sales, setSales] = useState([]);
  const [monthlySummary, setMonthlySummary] = useState({ currentMonth: 0, previousMonth: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSales = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/sales', { params });
      // API returns { data: { orders: [...], current_month_total, previous_month_total } }
      const payload = response.data?.data ?? response.data ?? {};
      const orders = payload.orders ?? [];
      const currentMonthTotal = payload.current_month_total ?? 0;
      const previousMonthTotal = payload.previous_month_total ?? 0;
      setSales(orders);
      setMonthlySummary({ currentMonth: currentMonthTotal, previousMonth: previousMonthTotal });
    } catch (err) {
      setError(
        err.response?.data?.error?.message ||
          'No se pudieron cargar las ventas. Intenta nuevamente.',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSales();
  }, [fetchSales]);

  /**
   * Filtra las ventas por rango de fechas.
   *
   * @param {string} from - Fecha de inicio (ISO string o YYYY-MM-DD).
   * @param {string} to - Fecha de fin (ISO string o YYYY-MM-DD).
   * @returns {Promise<void>}
   */
  const filterByDateRange = useCallback(
    (from, to) => {
      const params = {};
      if (from) params.from_date = from;
      if (to) params.to_date = to;
      return fetchSales(params);
    },
    [fetchSales],
  );

  return { sales, monthlySummary, loading, error, filterByDateRange };
}
