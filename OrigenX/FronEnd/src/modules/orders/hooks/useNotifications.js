/**
 * hooks/useNotifications.js – Hook para notificaciones en tiempo real via Firestore.
 *
 * Tarea 14.2 – Requerimiento: 19.2
 *
 * Escucha la colección `notifications` en tiempo real con onSnapshot.
 * Provee: { notifications, unreadCount, markAsRead }
 */

import { useCallback, useEffect, useState } from 'react';
import {
  collection,
  doc,
  onSnapshot,
  orderBy,
  query,
  updateDoc,
  where,
} from 'firebase/firestore';
import { db } from '../../../config/firebase';
import { useAuth } from '../../../context/AuthContext';

/**
 * Hook para escuchar notificaciones del usuario autenticado en tiempo real.
 *
 * @returns {{ notifications, unreadCount, markAsRead }}
 */
export function useNotifications() {
  const { currentUser } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!currentUser) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }

    // Consulta: notificaciones del usuario ordenadas por fecha descendente
    const q = query(
      collection(db, 'notifications'),
      where('userId', '==', currentUser.uid),
      orderBy('createdAt', 'desc'),
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const docs = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
        setNotifications(docs);
        setUnreadCount(docs.filter((n) => !n.read).length);
      },
      (err) => {
        // Error silencioso – las notificaciones no son críticas
        console.error('Error al escuchar notificaciones:', err);
      },
    );

    return () => unsubscribe();
  }, [currentUser]);

  /**
   * Marca una notificación como leída.
   *
   * @param {string} notificationId - ID del documento en Firestore.
   * @returns {Promise<void>}
   */
  const markAsRead = useCallback(async (notificationId) => {
    try {
      await updateDoc(doc(db, 'notifications', notificationId), { read: true });
    } catch (err) {
      console.error('Error al marcar notificación como leída:', err);
    }
  }, []);

  return { notifications, unreadCount, markAsRead };
}
