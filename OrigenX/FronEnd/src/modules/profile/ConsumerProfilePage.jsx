/**
 * ConsumerProfilePage.jsx – Perfil del consumidor.
 *
 * Muestra:
 *   - Información básica del usuario (nombre, email, rol)
 *   - Gestión de direcciones de envío (listar, agregar, eliminar)
 *
 * Solo accesible para usuarios con rol CONSUMER.
 */

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../context/AuthContext';
import apiClient from '../../config/axios';
import styles from './profile.module.css';

/* ── Íconos SVG ── */
function MapPinIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/>
      <circle cx="12" cy="10" r="3"/>
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 12h14"/><path d="M12 5v14"/>
    </svg>
  );
}

function UserIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  );
}

/* ── Componente de dirección ── */
function AddressCard({ address, onDelete, deleting }) {
  return (
    <div className={styles.addressCard}>
      <div className={styles.addressInfo}>
        <div className={styles.addressIconBox}>
          <MapPinIcon />
        </div>
        <div className={styles.addressText}>
          <p className={styles.addressStreet}>{address.street}</p>
          <p className={styles.addressDetail}>
            {address.city}, {address.department}
            {(address.postalCode || address.postal_code)
              ? ` – CP ${address.postalCode || address.postal_code}`
              : ''}
          </p>
        </div>
      </div>
      <button
        type="button"
        className={styles.deleteButton}
        onClick={() => onDelete(address.id)}
        disabled={deleting === address.id}
        aria-label={`Eliminar dirección ${address.street}`}
      >
        <TrashIcon />
      </button>
    </div>
  );
}

/* ── Formulario de nueva dirección ── */
function AddressForm({ onSave, onCancel, saving }) {
  const { register, handleSubmit, formState: { errors } } = useForm();

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSave)} noValidate>
      <div className={styles.fieldGroup}>
        <label htmlFor="street" className={styles.label}>
          Calle / Dirección <span className={styles.required}>*</span>
        </label>
        <input
          id="street"
          type="text"
          placeholder="Ej: Calle 10 # 5-23"
          className={`${styles.input} ${errors.street ? styles.inputError : ''}`}
          {...register('street', { required: 'La dirección es obligatoria' })}
        />
        {errors.street && <span className={styles.errorMessage} role="alert">{errors.street.message}</span>}
      </div>

      <div className={styles.fieldRow}>
        <div className={styles.fieldGroup}>
          <label htmlFor="city" className={styles.label}>
            Ciudad <span className={styles.required}>*</span>
          </label>
          <input
            id="city"
            type="text"
            placeholder="Ej: Pasto"
            className={`${styles.input} ${errors.city ? styles.inputError : ''}`}
            {...register('city', { required: 'La ciudad es obligatoria' })}
          />
          {errors.city && <span className={styles.errorMessage} role="alert">{errors.city.message}</span>}
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="department" className={styles.label}>
            Departamento <span className={styles.required}>*</span>
          </label>
          <input
            id="department"
            type="text"
            placeholder="Ej: Nariño"
            className={`${styles.input} ${errors.department ? styles.inputError : ''}`}
            {...register('department', { required: 'El departamento es obligatorio' })}
          />
          {errors.department && <span className={styles.errorMessage} role="alert">{errors.department.message}</span>}
        </div>
      </div>

      <div className={styles.fieldGroup}>
        <label htmlFor="postalCode" className={styles.label}>Código postal</label>
        <input
          id="postalCode"
          type="text"
          placeholder="Ej: 520001 (opcional)"
          className={styles.input}
          {...register('postalCode')}
        />
      </div>

      <div className={styles.formActions}>
        <button type="button" className={styles.cancelButton} onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className={styles.primaryButton} disabled={saving}>
          {saving ? 'Guardando…' : 'Guardar dirección'}
        </button>
      </div>
    </form>
  );
}

/* ── Página principal ── */
export default function ConsumerProfilePage() {
  const { currentUser, userRole } = useAuth();
  const [addresses, setAddresses] = useState([]);
  const [loadingAddresses, setLoadingAddresses] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [feedback, setFeedback] = useState(null); // { type, message }

  const userName = currentUser?.displayName || currentUser?.email || '';
  const userEmail = currentUser?.email || '';
  const initials = userName.split(' ').slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('');

  /* Cargar direcciones */
  useEffect(() => {
    apiClient.get('/api/addresses')
      .then(res => setAddresses(res.data?.data ?? []))
      .catch(() => setFeedback({ type: 'error', message: 'No se pudieron cargar las direcciones.' }))
      .finally(() => setLoadingAddresses(false));
  }, []);

  /* Guardar nueva dirección */
  const handleSaveAddress = async (data) => {
    setSaving(true);
    setFeedback(null);
    try {
      const res = await apiClient.post('/api/addresses', {
        street: data.street,
        city: data.city,
        department: data.department,
        postal_code: data.postalCode || null,
      });
      const newAddress = res.data?.data ?? res.data;
      setAddresses(prev => [...prev, newAddress]);
      setShowForm(false);
      setFeedback({ type: 'success', message: 'Dirección guardada correctamente.' });
      setTimeout(() => setFeedback(null), 4000);
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.error?.message || 'No se pudo guardar la dirección.',
      });
    } finally {
      setSaving(false);
    }
  };

  /* Eliminar dirección */
  const handleDeleteAddress = async (addressId) => {
    setDeleting(addressId);
    setFeedback(null);
    try {
      await apiClient.delete(`/api/addresses/${addressId}`);
      setAddresses(prev => prev.filter(a => a.id !== addressId));
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.error?.message || 'No se pudo eliminar la dirección.',
      });
    } finally {
      setDeleting(null);
    }
  };

  return (
    <main className={styles.page}>
      <div className={styles.container}>

        {/* Encabezado */}
        <header className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>Mi perfil</h1>
          <p className={styles.pageSubtitle}>Gestiona tu información personal y direcciones de envío.</p>
        </header>

        {/* Información del usuario */}
        <section className={styles.section} aria-labelledby="user-info-title">
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle} id="user-info-title">Información de cuenta</h2>
          </div>
          <div className={styles.userInfoCard}>
            <div className={styles.userAvatar} aria-hidden="true">
              {initials || <UserIcon />}
            </div>
            <div>
              <p className={styles.userInfoName}>{userName}</p>
              <p className={styles.userInfoEmail}>{userEmail}</p>
              <span className={styles.userRoleBadge}>Consumidor</span>
            </div>
          </div>
        </section>

        {/* Direcciones de envío */}
        <section className={styles.section} aria-labelledby="addresses-title">
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle} id="addresses-title">
              Direcciones de envío
              {addresses.length > 0 && (
                <span style={{ marginLeft: 8, fontSize: '0.875rem', fontWeight: 400, color: 'var(--color-text-secondary)' }}>
                  ({addresses.length}/5)
                </span>
              )}
            </h2>
            {!showForm && addresses.length < 5 && (
              <button
                type="button"
                className={styles.addButton}
                onClick={() => setShowForm(true)}
              >
                <PlusIcon /> Agregar
              </button>
            )}
          </div>

          {/* Feedback */}
          {feedback && (
            <div className={feedback.type === 'success' ? styles.successBanner : styles.errorBanner} role="alert">
              {feedback.message}
            </div>
          )}

          {/* Formulario nueva dirección */}
          {showForm && (
            <div style={{ marginBottom: 'var(--spacing-4)' }}>
              <AddressForm
                onSave={handleSaveAddress}
                onCancel={() => setShowForm(false)}
                saving={saving}
              />
            </div>
          )}

          {/* Lista de direcciones */}
          {loadingAddresses ? (
            <div style={{ padding: 'var(--spacing-6)', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
              Cargando direcciones…
            </div>
          ) : addresses.length === 0 && !showForm ? (
            <div className={styles.emptyAddresses}>
              <div className={styles.emptyAddressesIcon}>
                <MapPinIcon />
              </div>
              <p style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--color-text-primary)' }}>
                Sin direcciones registradas
              </p>
              <p style={{ fontSize: 'var(--font-size-sm)' }}>
                Agrega una dirección para agilizar tus pedidos.
              </p>
            </div>
          ) : (
            <div className={styles.addressList}>
              {addresses.map(addr => (
                <AddressCard
                  key={addr.id}
                  address={addr}
                  onDelete={handleDeleteAddress}
                  deleting={deleting}
                />
              ))}
            </div>
          )}
        </section>

      </div>
    </main>
  );
}
