/**
 * ProducerModule.jsx – Módulo principal del productor.
 *
 * Tarea 14.1 – Requerimientos: 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 7.1–7.3, 8.1, 8.2, 16.1–16.3
 *
 * Pestañas: Mi Perfil | Mis Productos | Mis Ventas
 * Solo accesible para usuarios con rol PRODUCER.
 */

import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import ProducerProfileForm from './components/ProducerProfileForm';
import ProductList from './components/ProductList';
import SalesPanel from './components/SalesPanel';
import styles from './producer.module.css';

const TABS = [
  { id: 'profile', label: 'Mi Perfil' },
  { id: 'products', label: 'Mis Productos' },
  { id: 'sales', label: 'Mis Ventas' },
];

export default function ProducerModule() {
  const { isProducer } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  // Acceso denegado si no es productor
  if (!isProducer) {
    return (
      <div className={styles.accessDenied} role="alert">
        <span className={styles.accessDeniedIcon} aria-hidden="true">🔒</span>
        <h1 className={styles.accessDeniedTitle}>Acceso restringido</h1>
        <p className={styles.accessDeniedText}>
          Esta sección es exclusiva para productores registrados. Si eres productor,
          asegúrate de haber iniciado sesión con tu cuenta correcta.
        </p>
      </div>
    );
  }

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        {/* Encabezado */}
        <header className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>Panel del Productor</h1>
          <p className={styles.pageSubtitle}>
            Gestiona tu perfil, productos y consulta tus ventas.
          </p>
        </header>

        {/* Navegación por pestañas */}
        <nav
          className={styles.tabNav}
          role="tablist"
          aria-label="Secciones del panel del productor"
        >
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`tabpanel-${tab.id}`}
              id={`tab-${tab.id}`}
              className={`${styles.tabButton} ${activeTab === tab.id ? styles.tabButtonActive : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Contenido de la pestaña activa */}
        <div
          id={`tabpanel-${activeTab}`}
          role="tabpanel"
          aria-labelledby={`tab-${activeTab}`}
        >
          {activeTab === 'profile' && <ProducerProfileForm />}
          {activeTab === 'products' && <ProductList />}
          {activeTab === 'sales' && <SalesPanel />}
        </div>
      </div>
    </main>
  );
}
