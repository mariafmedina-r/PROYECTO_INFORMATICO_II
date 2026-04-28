/**
 * CheckoutModule.jsx – Módulo de checkout en 3 pasos.
 *
 * Paso 1: Resumen + selección de envío
 * Paso 2: Pago simulado con tarjeta
 * Paso 3: Confirmación del pedido
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useCart } from '../../context/CartContext';
import apiClient from '../../config/axios';
import { formatPrice } from '../catalog/utils/formatPrice';
import styles from './checkout.module.css';

/* ── Íconos SVG ── */
function TruckIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v3"/>
      <rect width="7" height="7" x="14" y="11" rx="1"/>
      <circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>
    </svg>
  );
}

function MapPinIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
    </svg>
  );
}

function CreditCardIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect width="20" height="14" x="2" y="5" rx="2"/>
      <line x1="2" x2="22" y1="10" y2="10"/>
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 6 9 17l-5-5"/>
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <path d="M12 9v4"/><path d="M12 17h.01"/>
    </svg>
  );
}

/* ── Stepper ── */
const STEPS = [
  { label: 'Envío' },
  { label: 'Pago' },
  { label: 'Confirmación' },
];

function Stepper({ current }) {
  return (
    <div className={styles.stepper} aria-label="Pasos del checkout">
      {STEPS.map((step, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', flex: i < STEPS.length - 1 ? 1 : 'none' }}>
          <div className={styles.stepItem}>
            <div className={`${styles.stepCircle} ${i < current ? styles.stepCircleDone : i === current ? styles.stepCircleActive : ''}`}>
              {i < current ? '✓' : i + 1}
            </div>
            <span className={`${styles.stepLabel} ${i === current ? styles.stepLabelActive : ''}`}>
              {step.label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`${styles.stepConnector} ${i < current ? styles.stepConnectorActive : ''}`} />
          )}
        </div>
      ))}
    </div>
  );
}

/* ── Panel de resumen lateral ── */
function OrderSummaryPanel({ items, total, shippingCost }) {
  const grandTotal = total + (shippingCost ?? 0);
  return (
    <aside className={styles.orderSummary} aria-label="Resumen del pedido">
      <h2 className={styles.summaryTitle}>Tu pedido</h2>
      <div className={styles.summaryItems}>
        {items.map(item => (
          <div key={item.id} className={styles.summaryItem}>
            <span className={styles.summaryItemName}>{item.product_name ?? item.productName}</span>
            <span className={styles.summaryItemQty}>×{item.quantity}</span>
            <span className={styles.summaryItemPrice}>{formatPrice((item.price ?? 0) * item.quantity)}</span>
          </div>
        ))}
      </div>
      <hr className={styles.summaryDivider} />
      <div className={styles.summaryRow}>
        <span>Subtotal</span>
        <span>{formatPrice(total)}</span>
      </div>
      <div className={styles.summaryRow}>
        <span>Envío</span>
        <span>{shippingCost != null ? formatPrice(shippingCost) : 'A calcular'}</span>
      </div>
      <hr className={styles.summaryDivider} />
      <div className={styles.summaryTotal}>
        <span>Total</span>
        <span className={styles.summaryTotalAmount}>{formatPrice(grandTotal)}</span>
      </div>
    </aside>
  );
}

/* ── Paso 1: Envío ── */
function StepShipping({ addresses, shippingOptions, selectedAddress, selectedShipping, onSelectAddress, onSelectShipping, onNext, onBack, total }) {
  const selectedOption = shippingOptions.find(o => o.id === selectedShipping);

  return (
    <div className={styles.layout}>
      <div>
        {/* Dirección */}
        <div className={styles.section} style={{ marginBottom: 'var(--spacing-4)' }}>
          <h2 className={styles.sectionTitle}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <MapPinIcon /> Dirección de envío
            </span>
          </h2>
          {addresses.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 'var(--spacing-6)', color: 'var(--color-text-secondary)' }}>
              <p>No tienes direcciones guardadas.</p>
              <Link to="/profile" style={{ color: 'var(--color-secondary)', fontWeight: 600 }}>+ Agregar dirección</Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
              {addresses.map(addr => (
                <label key={addr.id}
                  className={`${styles.shippingOption} ${selectedAddress === addr.id ? styles.shippingOptionSelected : ''}`}>
                  <input type="radio" name="address" value={addr.id}
                    checked={selectedAddress === addr.id}
                    onChange={() => onSelectAddress(addr.id)}
                    className={styles.shippingRadio} />
                  <div className={styles.addressIconBox}><MapPinIcon /></div>
                  <div>
                    <div className={styles.shippingName}>{addr.street}</div>
                    <div className={styles.shippingDesc}>{addr.city}, {addr.department}{(addr.postalCode || addr.postal_code) ? ` – CP ${addr.postalCode || addr.postal_code}` : ''}</div>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Empresa de envío */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <TruckIcon /> Empresa de envío
            </span>
          </h2>
          <div className={styles.shippingOptions}>
            {shippingOptions.map(opt => (
              <label key={opt.id}
                className={`${styles.shippingOption} ${selectedShipping === opt.id ? styles.shippingOptionSelected : ''}`}>
                <input type="radio" name="shipping" value={opt.id}
                  checked={selectedShipping === opt.id}
                  onChange={() => onSelectShipping(opt.id)}
                  className={styles.shippingRadio} />
                <div className={styles.shippingIconBox}><TruckIcon /></div>
                <div className={styles.shippingInfo}>
                  <div className={styles.shippingName}>{opt.name}</div>
                  <div className={styles.shippingDesc}>{opt.description}</div>
                </div>
                <div className={styles.shippingCost}>{formatPrice(opt.cost)}</div>
              </label>
            ))}
          </div>
        </div>

        <div className={styles.actions}>
          <Link to="/cart" className={styles.secondaryButton}>← Volver al carrito</Link>
          <button type="button" className={styles.primaryButton}
            onClick={onNext}
            disabled={!selectedAddress || !selectedShipping}>
            Continuar al pago →
          </button>
        </div>
      </div>

      <OrderSummaryPanel items={[]} total={total} shippingCost={selectedOption?.cost ?? null} />
    </div>
  );
}

/* ── Paso 2: Pago ── */
function StepPayment({ items, total, shippingCost, selectedAddress, addresses, selectedShipping, shippingOptions, orderId, onOrderCreated, onBack }) {
  const { register, handleSubmit, formState: { errors }, watch } = useForm();
  const [submitting, setSubmitting] = useState(false);
  const [payError, setPayError] = useState(null);
  const navigate = useNavigate();
  const { refetchCart } = useCart();

  const addr = addresses.find(a => a.id === selectedAddress);
  const ship = shippingOptions.find(o => o.id === selectedShipping);
  const grandTotal = total + (ship?.cost ?? 0);

  const onSubmit = async (data) => {
    setSubmitting(true);
    setPayError(null);

    try {
      // 1. Crear la orden
      const orderRes = await apiClient.post('/api/orders', {
        address_id: selectedAddress,
        shipping_company: selectedShipping,
      });
      const order = orderRes.data?.data ?? orderRes.data;

      // 2. Simular el pago
      await apiClient.post('/api/payments/simulate', {
        order_id: order.id,
        card_number: data.cardNumber.replace(/\s/g, ''),
        card_holder: data.cardHolder,
        expiry_date: data.expiryDate,
        cvv: data.cvv,
        amount: grandTotal,
      });

      // 3. Refrescar carrito (ya fue vaciado por el backend)
      await refetchCart();

      // 4. Ir a confirmación
      onOrderCreated(order);
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'No se pudo procesar el pago. Intenta nuevamente.';
      setPayError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.layout}>
      <div>
        {/* Resumen de dirección y envío */}
        <div className={styles.section} style={{ marginBottom: 'var(--spacing-4)' }}>
          <h2 className={styles.sectionTitle}>Resumen de envío</h2>
          {addr && (
            <div className={styles.selectedAddressCard}>
              <div className={styles.addressIconBox}><MapPinIcon /></div>
              <div className={styles.addressText}>
                <strong>{addr.street}</strong>
                <span>{addr.city}, {addr.department}</span>
              </div>
            </div>
          )}
          {ship && (
            <div className={styles.selectedAddressCard}>
              <div className={styles.addressIconBox}><TruckIcon /></div>
              <div className={styles.addressText}>
                <strong>{ship.name}</strong>
                <span>{ship.description} — {formatPrice(ship.cost)}</span>
              </div>
            </div>
          )}
        </div>

        {/* Formulario de pago */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <CreditCardIcon /> Datos de pago
            </span>
          </h2>

          <div className={styles.simulationNote}>
            <AlertIcon />
            <span>
              <strong>Modo simulación.</strong> Usa cualquier número de 16 dígitos.
              Terminar en <code>0000</code> simula un pago fallido.
            </span>
          </div>

          <form className={styles.paymentForm} onSubmit={handleSubmit(onSubmit)} noValidate style={{ marginTop: 'var(--spacing-4)' }}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>
                Número de tarjeta <span className={styles.required}>*</span>
              </label>
              <div className={styles.cardBrands}>
                <span className={`${styles.cardBrand} ${styles.cardBrandVisa}`}>VISA</span>
                <span className={`${styles.cardBrand} ${styles.cardBrandMC}`}>MC</span>
              </div>
              <input type="text" placeholder="1234 5678 9012 3456" maxLength={19}
                className={`${styles.input} ${errors.cardNumber ? styles.inputError : ''}`}
                {...register('cardNumber', {
                  required: 'El número de tarjeta es obligatorio',
                  validate: v => v.replace(/\s/g, '').length === 16 || 'Debe tener 16 dígitos',
                })}
                onChange={e => {
                  const v = e.target.value.replace(/\D/g, '').slice(0, 16);
                  e.target.value = v.replace(/(.{4})/g, '$1 ').trim();
                }}
              />
              {errors.cardNumber && <span className={styles.errorMessage}>{errors.cardNumber.message}</span>}
            </div>

            <div className={styles.fieldGroup}>
              <label className={styles.label}>Titular de la tarjeta <span className={styles.required}>*</span></label>
              <input type="text" placeholder="NOMBRE APELLIDO"
                className={`${styles.input} ${errors.cardHolder ? styles.inputError : ''}`}
                style={{ textTransform: 'uppercase' }}
                {...register('cardHolder', { required: 'El nombre del titular es obligatorio' })} />
              {errors.cardHolder && <span className={styles.errorMessage}>{errors.cardHolder.message}</span>}
            </div>

            <div className={styles.fieldRow}>
              <div className={styles.fieldGroup}>
                <label className={styles.label}>Vencimiento <span className={styles.required}>*</span></label>
                <input type="text" placeholder="MM/YY" maxLength={5}
                  className={`${styles.input} ${errors.expiryDate ? styles.inputError : ''}`}
                  {...register('expiryDate', {
                    required: 'La fecha de vencimiento es obligatoria',
                    pattern: { value: /^\d{2}\/\d{2}$/, message: 'Formato MM/YY' },
                  })}
                  onChange={e => {
                    let v = e.target.value.replace(/\D/g, '').slice(0, 4);
                    if (v.length > 2) v = v.slice(0, 2) + '/' + v.slice(2);
                    e.target.value = v;
                  }}
                />
                {errors.expiryDate && <span className={styles.errorMessage}>{errors.expiryDate.message}</span>}
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.label}>CVV <span className={styles.required}>*</span></label>
                <input type="password" placeholder="•••" maxLength={4}
                  className={`${styles.input} ${errors.cvv ? styles.inputError : ''}`}
                  {...register('cvv', {
                    required: 'El CVV es obligatorio',
                    minLength: { value: 3, message: 'Mínimo 3 dígitos' },
                  })} />
                {errors.cvv && <span className={styles.errorMessage}>{errors.cvv.message}</span>}
              </div>
            </div>

            {payError && (
              <div className={styles.errorBanner} role="alert">
                <AlertIcon />
                <span>{payError}</span>
              </div>
            )}

            <div className={styles.actions}>
              <button type="button" className={styles.secondaryButton} onClick={onBack} disabled={submitting}>
                ← Atrás
              </button>
              <button type="submit" className={styles.primaryButton} disabled={submitting}>
                {submitting ? 'Procesando…' : `Pagar ${formatPrice(grandTotal)}`}
              </button>
            </div>
          </form>
        </div>
      </div>

      <OrderSummaryPanel items={items} total={total} shippingCost={ship?.cost ?? null} />
    </div>
  );
}

/* ── Paso 3: Confirmación ── */
function StepConfirmation({ order }) {
  return (
    <div className={styles.confirmationPage}>
      <div className={styles.confirmationIcon}>
        <CheckIcon />
      </div>
      <h2 className={styles.confirmationTitle}>¡Pedido confirmado!</h2>
      <p className={styles.confirmationSubtitle}>
        Tu pago fue procesado exitosamente. Recibirás actualizaciones del estado de tu pedido en la sección <strong>Mis pedidos</strong>.
      </p>
      <div className={styles.confirmationOrderId}>
        <span>Número de pedido:</span>
        <span className={styles.confirmationOrderIdValue}>
          {order?.id?.slice(0, 8).toUpperCase() ?? '—'}
        </span>
      </div>
      <div className={styles.confirmationActions}>
        <Link to="/orders" className={styles.confirmationPrimaryBtn}>Ver mis pedidos</Link>
        <Link to="/catalog" className={styles.confirmationSecondaryBtn}>Seguir comprando</Link>
      </div>
    </div>
  );
}

/* ── Módulo principal ── */
export default function CheckoutModule() {
  const { items, total } = useCart();
  const navigate = useNavigate();
  const location = useLocation();
  const preselectedAddressId = location.state?.addressId ?? null;

  const [step, setStep] = useState(0);
  const [addresses, setAddresses] = useState([]);
  const [shippingOptions, setShippingOptions] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [selectedShipping, setSelectedShipping] = useState(null);
  const [confirmedOrder, setConfirmedOrder] = useState(null);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    Promise.all([
      apiClient.get('/api/addresses'),
      apiClient.get('/api/shipping/options'),
    ]).then(([addrRes, shipRes]) => {
      const addrList = addrRes.data?.data ?? [];
      const shipList = shipRes.data?.data ?? shipRes.data ?? [];
      setAddresses(addrList);
      setShippingOptions(shipList);
      // Preseleccionar la dirección que venía del carrito, o la primera disponible
      if (preselectedAddressId && addrList.find(a => a.id === preselectedAddressId)) {
        setSelectedAddress(preselectedAddressId);
      } else if (addrList.length > 0) {
        setSelectedAddress(addrList[0].id);
      }
      if (shipList.length > 0) setSelectedShipping(shipList[0].id);
    }).catch(() => {}).finally(() => setLoadingData(false));
  }, []);

  // Si el carrito está vacío y no hay orden confirmada, redirigir
  useEffect(() => {
    if (!loadingData && items.length === 0 && !confirmedOrder) {
      navigate('/cart');
    }
  }, [items, loadingData, confirmedOrder, navigate]);

  const selectedShipOption = shippingOptions.find(o => o.id === selectedShipping);

  if (loadingData) {
    return (
      <main className={styles.page}>
        <div className={styles.container}>
          <div style={{ padding: 'var(--spacing-16)', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
            Cargando…
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        <header className={styles.pageHeader}>
          <h1 className={styles.pageTitle}>Checkout</h1>
        </header>

        <Stepper current={step} />

        {step === 0 && (
          <StepShipping
            addresses={addresses}
            shippingOptions={shippingOptions}
            selectedAddress={selectedAddress}
            selectedShipping={selectedShipping}
            onSelectAddress={setSelectedAddress}
            onSelectShipping={setSelectedShipping}
            onNext={() => setStep(1)}
            total={total}
          />
        )}

        {step === 1 && (
          <StepPayment
            items={items}
            total={total}
            shippingCost={selectedShipOption?.cost ?? 0}
            selectedAddress={selectedAddress}
            addresses={addresses}
            selectedShipping={selectedShipping}
            shippingOptions={shippingOptions}
            onOrderCreated={(order) => { setConfirmedOrder(order); setStep(2); }}
            onBack={() => setStep(0)}
          />
        )}

        {step === 2 && <StepConfirmation order={confirmedOrder} />}
      </div>
    </main>
  );
}
