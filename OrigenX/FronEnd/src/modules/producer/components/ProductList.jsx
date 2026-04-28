/**
 * components/ProductList.jsx – Lista de productos del productor con acciones.
 *
 * Tarea 14.1 – Requerimientos: 5.1, 6.1, 8.1, 8.2
 *
 * Muestra: nombre, precio, badge de estado, botón editar, botón activar/desactivar.
 */

import { useState } from 'react';
import { useProducerProducts } from '../hooks/useProducerProducts';
import ProductForm from './ProductForm';
import styles from '../producer.module.css';

/** Formatea precio en COP */
function formatPrice(price) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
  }).format(price);
}

export default function ProductList() {
  const {
    products,
    loading,
    error,
    createProductOnly,
    updateProductOnly,
    toggleStatus,
    uploadImageOnly,
    deleteImageOnly,
    getProductDetail,
    refetch,
  } = useProducerProducts();

  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);
  const [togglingId, setTogglingId] = useState(null);

  const handleNewProduct = () => {
    setEditingProduct(null);
    setFormError(null);
    setShowForm(true);
  };

  const handleEditProduct = async (product) => {
    setFormError(null);
    try {
      // Cargar el producto completo con descripción e imágenes
      const full = await getProductDetail(product.id);
      setEditingProduct(full);
    } catch {
      setEditingProduct(product); // fallback con datos básicos
    }
    setShowForm(true);
  };

  const handleFormSubmit = async (data) => {
    setSaving(true);
    setFormError(null);
    try {
      if (editingProduct) {
        // 1. Actualizar datos sin refetch
        await updateProductOnly(editingProduct.id, data);
        // 2. Eliminar imágenes marcadas sin refetch intermedio
        if (data._deletedIds?.length) {
          for (const imgId of data._deletedIds) {
            try { await deleteImageOnly(editingProduct.id, imgId); } catch { /* continuar */ }
          }
        }
        // 3. Subir imágenes nuevas sin refetch intermedio
        if (data._newFiles?.length) {
          for (const file of data._newFiles) {
            try { await uploadImageOnly(editingProduct.id, file); } catch { /* continuar */ }
          }
        }
      } else {
        // 1. Crear producto sin refetch
        const created = await createProductOnly(data);
        const productId = created?.data?.id ?? created?.id;
        // 2. Subir imágenes sin refetch intermedio
        if (productId && data._newFiles?.length) {
          for (const file of data._newFiles) {
            try { await uploadImageOnly(productId, file); } catch { /* continuar */ }
          }
        }
      }
      // 4. Cerrar modal y hacer UN solo refetch al final
      setShowForm(false);
      setEditingProduct(null);
      await refetch();
    } catch (err) {
      setFormError(
        err.response?.data?.error?.message ||
          'No se pudo guardar el producto. Intenta nuevamente.',
      );
    } finally {
      setSaving(false);
    }
  };

  const handleToggleStatus = async (product) => {
    const newStatus = product.status === 'active' ? 'inactive' : 'active';
    setTogglingId(product.id);
    try {
      await toggleStatus(product.id, newStatus);
    } catch {
      // Error silencioso – refetch para sincronizar
      await refetch();
    } finally {
      setTogglingId(null);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingProduct(null);
    setFormError(null);
  };

  if (loading) {
    return (
      <div className={styles.loadingState} aria-busy="true">
        {[1, 2, 3].map((i) => (
          <div key={i} className={styles.skeletonBlock} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState} role="alert">
        <span className={styles.errorStateIcon}>⚠️</span>
        <p className={styles.errorStateText}>{error}</p>
        <button type="button" className={styles.retryButton} onClick={refetch}>
          Intentar nuevamente
        </button>
      </div>
    );
  }

  return (
    <section className={styles.productListSection}>
      {/* Encabezado con botón de nuevo producto */}
      <div className={styles.listHeader}>
        <h2 className={styles.sectionTitle}>Mis Productos</h2>
        <button
          type="button"
          className={styles.primaryButton}
          onClick={handleNewProduct}
        >
          + Nuevo Producto
        </button>
      </div>

      {/* Error del formulario */}
      {formError && (
        <div className={styles.serverError} role="alert">
          {formError}
        </div>
      )}

      {/* Lista vacía */}
      {products.length === 0 && (
        <div className={styles.emptyState} role="status">
          <span className={styles.emptyStateIcon}>📦</span>
          <h3 className={styles.emptyStateTitle}>Sin productos</h3>
          <p className={styles.emptyStateText}>
            Aún no has registrado ningún producto. Haz clic en &quot;Nuevo Producto&quot; para comenzar.
          </p>
        </div>
      )}

      {/* Aviso si hay productos inactivos */}
      {products.some(p => p.status === 'inactive') && (
        <div className={styles.infoMessage} role="note" style={{ marginBottom: 'var(--spacing-4)' }}>
          ⚠️ Tienes productos <strong>inactivos</strong> que no son visibles en el catálogo ni en tu perfil público. Usa el botón <strong>"Activar"</strong> para publicarlos.
        </div>
      )}

      {/* Tabla de productos */}
      {products.length > 0 && (
        <div className={styles.tableWrapper}>
          <table className={styles.table} aria-label="Lista de productos">
            <thead>
              <tr>
                <th className={`${styles.th} ${styles.thCenter}`}>Nombre</th>
                <th className={`${styles.th} ${styles.thCenter}`}>Precio</th>
                <th className={`${styles.th} ${styles.thCenter}`}>Stock</th>
                <th className={`${styles.th} ${styles.thCenter}`}>Estado</th>
                <th className={`${styles.th} ${styles.thActions}`}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id} className={styles.tr}>
                  <td className={styles.td}>
                    <span className={styles.productName}>{product.name}</span>
                  </td>
                  <td className={styles.td}>
                    <span className={styles.productPrice}>
                      {formatPrice(product.price)}
                    </span>
                  </td>
                  <td className={styles.td}>
                    <span
                      className={
                        (product.stock ?? 0) > 0
                          ? styles.stockAvailable
                          : styles.stockEmpty
                      }
                    >
                      {product.stock ?? 0}
                    </span>
                  </td>
                  <td className={styles.td}>
                    <span
                      className={`${styles.statusBadge} ${
                        product.status === 'active'
                          ? styles.statusActive
                          : styles.statusInactive
                      }`}
                    >
                      {product.status === 'active' ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className={styles.td}>
                    <div className={styles.actionButtons}>
                      <button
                        type="button"
                        className={styles.editButton}
                        onClick={() => handleEditProduct(product)}
                        aria-label={`Editar ${product.name}`}
                      >
                        ✏️ Editar
                      </button>
                      <button
                        type="button"
                        className={`${styles.toggleButton} ${
                          product.status === 'active'
                            ? styles.toggleButtonDeactivate
                            : styles.toggleButtonActivate
                        }`}
                        onClick={() => handleToggleStatus(product)}
                        disabled={togglingId === product.id}
                        aria-label={
                          product.status === 'active'
                            ? `Desactivar ${product.name}`
                            : `Activar ${product.name}`
                        }
                      >
                        {togglingId === product.id
                          ? '...'
                          : product.status === 'active'
                          ? 'Desactivar'
                          : 'Activar'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal del formulario */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onSubmit={handleFormSubmit}
          onCancel={handleCancel}
          uploadImage={uploadImageOnly}
          saving={saving}
        />
      )}
    </section>
  );
}
