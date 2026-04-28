// Configuración de Axios – cliente HTTP para el backend Python
import axios from 'axios';
import { auth } from './firebase';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    // Bypass ngrok browser warning page (necesario cuando el backend corre detrás de ngrok)
    'ngrok-skip-browser-warning': 'true',
  },
  timeout: 10000,
});

// Interceptor de solicitud: adjuntar Firebase ID Token en cada petición
apiClient.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Interceptor de respuesta: manejo centralizado de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado – redirigir al login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default apiClient;
