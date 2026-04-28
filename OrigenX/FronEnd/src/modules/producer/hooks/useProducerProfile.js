/**
 * hooks/useProducerProfile.js – Hook para gestión del perfil del productor.
 */

import { useCallback, useEffect, useState } from 'react';
import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';
import apiClient from '../../../config/axios';
import { useAuth } from '../../../context/AuthContext';
import { storage } from '../../../config/firebase';

const MAX_IMAGES = 6;
const MAX_SIZE_MB = 2;

export function useProducerProfile() {
  const { currentUser } = useAuth();
  const [profile, setProfile]   = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const fetchProfile = useCallback(async () => {
    if (!currentUser) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/api/producers/${currentUser.uid}`);
      setProfile(response.data?.data ?? response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setProfile(null);
      } else {
        setError(
          err.response?.data?.error?.message ||
            'No se pudo cargar el perfil. Intenta nuevamente.',
        );
      }
    } finally {
      setLoading(false);
    }
  }, [currentUser]);

  useEffect(() => { fetchProfile(); }, [fetchProfile]);

  /**
   * Sube archivos nuevos a Firebase Storage y devuelve sus URLs.
   * @param {File[]} files
   * @returns {Promise<string[]>}
   */
  const uploadImages = useCallback(
    async (files) => {
      const urls = [];
      for (const file of files) {
        if (file.size > MAX_SIZE_MB * 1024 * 1024) {
          throw new Error(`La imagen "${file.name}" supera los ${MAX_SIZE_MB} MB.`);
        }
        const path = `producers/${currentUser.uid}/${Date.now()}_${file.name}`;
        const storageRef = ref(storage, path);
        await uploadBytes(storageRef, file);
        const url = await getDownloadURL(storageRef);
        urls.push(url);
      }
      return urls;
    },
    [currentUser],
  );

  /**
   * Elimina una imagen de Firebase Storage por su URL.
   * @param {string} url
   */
  const deleteImage = useCallback(async (url) => {
    try {
      const storageRef = ref(storage, url);
      await deleteObject(storageRef);
    } catch {
      // Si ya no existe en storage, ignorar
    }
  }, []);

  /**
   * Actualiza el perfil del productor.
   * Convierte camelCase del frontend a snake_case que espera el backend.
   */
  const updateProfile = useCallback(
    async (data) => {
      if (!currentUser) throw new Error('No autenticado');
      const payload = {
        farm_name:            data.farmName,
        region:               data.region,
        description:          data.description,
        whatsapp:             data.whatsapp,
        show_register_email:  data.showRegisterEmail ?? true,
        alt_email:            data.altEmail ?? null,
        show_alt_email:       data.showAltEmail ?? false,
        images:               data.images ?? [],
      };
      const response = await apiClient.put(`/api/producers/${currentUser.uid}`, payload);
      setProfile(response.data?.data ?? response.data);
    },
    [currentUser],
  );

  /**
   * Activa o desactiva la visibilidad del perfil en el catálogo.
   * @param {boolean} isActive
   */
  const setVisibility = useCallback(
    async (isActive) => {
      if (!currentUser) throw new Error('No autenticado');
      const response = await apiClient.patch(`/api/producers/${currentUser.uid}/visibility`, { is_active: isActive });
      setProfile(response.data?.data ?? response.data);
    },
    [currentUser],
  );

  return {
    profile,
    loading,
    error,
    updateProfile,
    uploadImages,
    deleteImage,
    setVisibility,
    refetch: fetchProfile,
    MAX_IMAGES,
    MAX_SIZE_MB,
  };
}
