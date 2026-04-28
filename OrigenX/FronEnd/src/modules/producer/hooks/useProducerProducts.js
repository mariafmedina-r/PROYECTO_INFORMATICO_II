/**
 * hooks/useProducerProducts.js – Hook para gestión de productos del productor.
 *
 * Tarea 14.1 – Requerimientos: 5.1, 5.2, 6.1, 6.2, 7.1, 7.2, 7.3, 8.1, 8.2
 *
 * Provee: { products, loading, error, createProduct, updateProduct, toggleStatus, uploadImage, deleteImage }
 */

import { useCallback, useEffect, useState } from 'react';
import apiClient from '../../../config/axios';
import { useAuth } from '../../../context/AuthContext';

/**
 * Hook para gestionar los productos del productor autenticado.
 *
 * @returns {{ products, loading, error, createProduct, updateProduct, toggleStatus, uploadImage, deleteImage, refetch }}
 */
export function useProducerProducts() {
  const { currentUser } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(async () => {
    if (!currentUser) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/products', {
        params: { producerId: currentUser.uid, page_size: 100, includeInactive: true },
      });
      setProducts(response.data?.data?.items ?? response.data?.items ?? []);
    } catch (err) {
      setError(
        err.response?.data?.error?.message ||
          'No se pudieron cargar los productos. Intenta nuevamente.',
      );
    } finally {
      setLoading(false);
    }
  }, [currentUser]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  /**
   * Obtiene el detalle completo de un producto (con descripción e imágenes).
   */
  const getProductDetail = useCallback(async (productId) => {
    const response = await apiClient.get(`/api/products/${productId}`);
    return response.data?.data ?? response.data;
  }, []);

  /**
   * Crea un nuevo producto sin hacer refetch automático.
   * Útil cuando se necesita subir imágenes después de crear.
   */
  const createProductOnly = useCallback(async (data) => {
    const response = await apiClient.post('/api/products', data);
    return response.data;
  }, []);

  /**
   * Crea un nuevo producto.
   */
  const createProduct = useCallback(async (data) => {
    const response = await apiClient.post('/api/products', data);
    await fetchProducts();
    return response.data;
  }, [fetchProducts]);

  /**
   * Actualiza un producto existente sin refetch automático.
   */
  const updateProductOnly = useCallback(async (productId, data) => {
    const response = await apiClient.put(`/api/products/${productId}`, data);
    return response.data;
  }, []);

  /**
   * Actualiza un producto existente.
   */
  const updateProduct = useCallback(async (productId, data) => {
    const response = await apiClient.put(`/api/products/${productId}`, data);
    await fetchProducts();
    return response.data;
  }, [fetchProducts]);

  /**
   * Activa o desactiva un producto.
   *
   * @param {string} productId
   * @param {'active' | 'inactive'} status
   * @returns {Promise<void>}
   */
  const toggleStatus = useCallback(async (productId, status) => {
    await apiClient.patch(`/api/products/${productId}/status`, { status });
    setProducts((prev) =>
      prev.map((p) => (p.id === productId ? { ...p, status } : p)),
    );
  }, []);

  /**
   * Sube una imagen a un producto (sin refetch automático).
   * Usar cuando se suben múltiples imágenes seguidas.
   */
  const uploadImageOnly = useCallback(async (productId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post(`/api/products/${productId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data?.data ?? response.data;
  }, []);

  /**
   * Sube una imagen a un producto.
   */
  const uploadImage = useCallback(async (productId, file) => {
    const formData = new FormData();
    formData.append('file', file);  // el backend espera el campo 'file'
    const response = await apiClient.post(`/api/products/${productId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    await fetchProducts();
    return response.data?.data ?? response.data;
  }, [fetchProducts]);

  /**
   * Elimina una imagen de un producto sin refetch automático.
   */
  const deleteImageOnly = useCallback(async (productId, imgId) => {
    await apiClient.delete(`/api/products/${productId}/images/${imgId}`);
  }, []);

  /**
   * Elimina una imagen de un producto.
   */
  const deleteImage = useCallback(async (productId, imgId) => {
    await apiClient.delete(`/api/products/${productId}/images/${imgId}`);
    await fetchProducts();
  }, [fetchProducts]);

  return {
    products,
    loading,
    error,
    createProduct,
    createProductOnly,
    updateProduct,
    updateProductOnly,
    toggleStatus,
    uploadImage,
    uploadImageOnly,
    deleteImage,
    deleteImageOnly,
    getProductDetail,
    refetch: fetchProducts,
  };
}
