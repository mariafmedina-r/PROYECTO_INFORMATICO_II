/**
 * context/AuthContext.jsx – Contexto global de autenticación.
 *
 * Provee el estado del usuario autenticado a toda la aplicación.
 * Usa Firebase Auth onAuthStateChanged para mantener el estado sincronizado.
 *
 * Tarea 2.9 – Requerimientos: 1.1, 2.1, 2.4, 12.5
 * RNF-003.2 – Cierre de sesión automático por inactividad (5 minutos).
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
} from 'firebase/auth';
import { auth } from '../config/firebase';
import apiClient from '../config/axios';

const AuthContext = createContext(null);

/** Tiempo de inactividad antes de cerrar sesión (5 minutos en ms) */
const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000;

/** Eventos del usuario que se consideran actividad */
const ACTIVITY_EVENTS = [
  'mousemove', 'mousedown', 'mouseup',
  'keydown', 'keyup', 'keypress',
  'touchstart', 'touchmove', 'touchend',
  'scroll', 'click', 'focus', 'input',
  'wheel', 'pointerdown', 'pointermove',
];

/**
 * Proveedor del contexto de autenticación.
 */
export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [producerFarmName, setProducerFarmName] = useState(null);
  const [loading, setLoading] = useState(true);
  const inactivityTimerRef = useRef(null);

  // Cierra sesión por inactividad
  const handleInactivityLogout = useCallback(async () => {
    await signOut(auth);
  }, []);

  // Reinicia el timer de inactividad
  const resetInactivityTimer = useCallback(() => {
    if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
    inactivityTimerRef.current = setTimeout(handleInactivityLogout, INACTIVITY_TIMEOUT_MS);
  }, [handleInactivityLogout]);

  // Arranca/detiene listeners según si hay sesión activa
  useEffect(() => {
    if (!currentUser) {
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
        inactivityTimerRef.current = null;
      }
      ACTIVITY_EVENTS.forEach(evt => document.removeEventListener(evt, resetInactivityTimer));
      document.removeEventListener('visibilitychange', resetInactivityTimer);
      return;
    }

    resetInactivityTimer();

    // Escuchar en document para capturar eventos de todos los elementos,
    // incluyendo iframes, contenteditable (Tiptap) y elementos con stopPropagation
    ACTIVITY_EVENTS.forEach(evt =>
      document.addEventListener(evt, resetInactivityTimer, { passive: true, capture: true })
    );

    // Resetear timer cuando el usuario vuelve a la pestaña
    document.addEventListener('visibilitychange', resetInactivityTimer);

    return () => {
      if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
      ACTIVITY_EVENTS.forEach(evt =>
        document.removeEventListener(evt, resetInactivityTimer, { capture: true })
      );
      document.removeEventListener('visibilitychange', resetInactivityTimer);
    };
  }, [currentUser, resetInactivityTimer]);

  // Escuchar cambios en el estado de autenticación de Firebase
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        const tokenResult = await firebaseUser.getIdTokenResult();
        const role = tokenResult.claims.role || null;
        setCurrentUser(firebaseUser);
        setUserRole(role);

        if (role === 'PRODUCER') {
          try {
            const res = await apiClient.get(`/api/producers/${firebaseUser.uid}`);
            const profile = res.data?.data ?? res.data;
            setProducerFarmName(profile?.farmName || null);
          } catch {
            setProducerFarmName(null);
          }
        } else {
          setProducerFarmName(null);
        }
      } else {
        setCurrentUser(null);
        setUserRole(null);
        setProducerFarmName(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const register = useCallback(async (name, email, password, role) => {
    await apiClient.post('/api/auth/register', { name, email, password, role });
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    await updateProfile(userCredential.user, { displayName: name });
  }, []);

  const login = useCallback(async (email, password) => {
    await signInWithEmailAndPassword(auth, email, password);
  }, []);

  const logout = useCallback(async () => {
    await signOut(auth);
  }, []);

  const forgotPassword = useCallback(async (email) => {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch {
      // Silenciar errores para no revelar si el correo existe (Req. 2.5)
    }
  }, []);

  const value = {
    currentUser,
    userRole,
    producerFarmName,
    loading,
    register,
    login,
    logout,
    forgotPassword,
    isAuthenticated: !!currentUser,
    isConsumer: userRole === 'CONSUMER',
    isProducer: userRole === 'PRODUCER',
    isAdmin: userRole === 'ADMIN',
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

/**
 * Hook para acceder al contexto de autenticación.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
}

export default AuthContext;
