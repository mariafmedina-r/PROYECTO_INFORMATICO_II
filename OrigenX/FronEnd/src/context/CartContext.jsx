/**
 * context/CartContext.jsx – Contexto global del carrito de compras.
 *
 * Tarea 13.1 – Requerimientos: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6
 *
 * Provee el estado del carrito a toda la aplicación:
 *   - items: lista de ítems del carrito
 *   - itemCount: número total de ítems (para el badge del navbar – Req. 12.4)
 *   - total: precio total del carrito
 *   - loading / error: estado de la petición
 *   - addItem, updateQuantity, removeItem, clearCart: operaciones CRUD
 *
 * El carrito se carga desde el backend al iniciar sesión y se limpia al cerrar sesión.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useReducer,
} from 'react';
import apiClient from '../config/axios';
import { useAuth } from './AuthContext';

/* ============================================================
   Estado y reducer
   ============================================================ */

const initialState = {
  items: [],
  loading: false,
  error: null,
};

function cartReducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, items: action.payload, error: null };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'SET_ITEMS':
      return { ...state, items: action.payload };
    case 'ADD_ITEM': {
      const existing = state.items.find((i) => i.id === action.payload.id);
      if (existing) {
        return {
          ...state,
          items: state.items.map((i) =>
            i.id === action.payload.id
              ? { ...i, quantity: action.payload.quantity }
              : i,
          ),
        };
      }
      return { ...state, items: [...state.items, action.payload] };
    }
    case 'UPDATE_ITEM':
      return {
        ...state,
        items: state.items.map((i) =>
          i.id === action.payload.id
            ? { ...i, quantity: action.payload.quantity }
            : i,
        ),
      };
    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter((i) => i.id !== action.payload),
      };
    case 'CLEAR':
      return { ...state, items: [] };
    default:
      return state;
  }
}

/* ============================================================
   Contexto
   ============================================================ */

const CartContext = createContext(null);

/**
 * Proveedor del contexto del carrito.
 * Debe estar dentro de AuthProvider.
 */
export function CartProvider({ children }) {
  const { isAuthenticated, isConsumer } = useAuth();
  const [state, dispatch] = useReducer(cartReducer, initialState);

  /* ----------------------------------------------------------
     Cargar carrito desde el backend al autenticarse (Req. 12.6)
     ---------------------------------------------------------- */
  const fetchCart = useCallback(async () => {
    if (!isAuthenticated || !isConsumer) {
      dispatch({ type: 'CLEAR' });
      return;
    }
    dispatch({ type: 'FETCH_START' });
    try {
      const response = await apiClient.get('/api/cart');
      // Backend devuelve { data: { items: [...], total, ... } }
      const cartData = response.data?.data ?? response.data;
      dispatch({ type: 'FETCH_SUCCESS', payload: cartData.items ?? [] });
    } catch (err) {
      dispatch({
        type: 'FETCH_ERROR',
        payload:
          err.response?.data?.error?.message ||
          'No se pudo cargar el carrito.',
      });
    }
  }, [isAuthenticated, isConsumer]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  /* ----------------------------------------------------------
     Agregar ítem al carrito (Req. 12.1)
     ---------------------------------------------------------- */
  const addItem = useCallback(
    async (productId, quantity = 1) => {
      try {
        const response = await apiClient.post('/api/cart/items', {
          product_id: productId,
          quantity,
        });
        // Backend devuelve { data: { items: [...], total, ... } }
        const cartData = response.data?.data ?? response.data;
        dispatch({ type: 'SET_ITEMS', payload: cartData.items ?? [] });
        return { success: true };
      } catch (err) {
        return {
          success: false,
          error:
            err.response?.data?.error?.message ||
            'No se pudo agregar el producto al carrito.',
        };
      }
    },
    [],
  );

  /* ----------------------------------------------------------
     Actualizar cantidad de un ítem (Req. 12.2)
     ---------------------------------------------------------- */
  const updateQuantity = useCallback(async (itemId, quantity) => {
    // Optimistic update
    dispatch({ type: 'UPDATE_ITEM', payload: { id: itemId, quantity } });
    try {
      const response = await apiClient.put(`/api/cart/items/${itemId}`, { quantity });
      const cartData = response.data?.data ?? response.data;
      dispatch({ type: 'SET_ITEMS', payload: cartData.items ?? [] });
      return { success: true };
    } catch (err) {
      await fetchCart();
      return {
        success: false,
        error:
          err.response?.data?.error?.message ||
          'No se pudo actualizar la cantidad.',
      };
    }
  }, [fetchCart]);

  /* ----------------------------------------------------------
     Eliminar ítem del carrito (Req. 12.3)
     ---------------------------------------------------------- */
  const removeItem = useCallback(async (itemId) => {
    // Optimistic update
    dispatch({ type: 'REMOVE_ITEM', payload: itemId });
    try {
      const response = await apiClient.delete(`/api/cart/items/${itemId}`);
      const cartData = response.data?.data ?? response.data;
      dispatch({ type: 'SET_ITEMS', payload: cartData.items ?? [] });
      return { success: true };
    } catch (err) {
      await fetchCart();
      return {
        success: false,
        error:
          err.response?.data?.error?.message ||
          'No se pudo eliminar el producto del carrito.',
      };
    }
  }, [fetchCart]);

  /* ----------------------------------------------------------
     Limpiar carrito localmente (al cerrar sesión, etc.)
     ---------------------------------------------------------- */
  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR' });
  }, []);

  /* ----------------------------------------------------------
     Valores derivados
     ---------------------------------------------------------- */
  const itemCount = state.items.reduce((sum, item) => sum + (item.quantity ?? 0), 0);
  const total = state.items.reduce(
    (sum, item) => sum + (item.price ?? 0) * (item.quantity ?? 0),
    0,
  );

  const value = {
    items: state.items,
    loading: state.loading,
    error: state.error,
    itemCount,
    total,
    addItem,
    updateQuantity,
    removeItem,
    clearCart,
    refetchCart: fetchCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

/**
 * Hook para acceder al contexto del carrito.
 *
 * @returns {object} Contexto del carrito.
 * @throws {Error} Si se usa fuera de CartProvider.
 */
export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart debe usarse dentro de un CartProvider');
  }
  return context;
}

export default CartContext;
