/**
 * components/RegisterForm.jsx – Formulario de registro de usuario.
 *
 * Tarea 2.9 – Requerimientos: 1.1, 1.3, 1.4, RNF-002.5, RNF-009.2
 *
 * Usa react-hook-form para validación en tiempo real.
 * Muestra mensajes de error descriptivos por campo.
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import styles from '../auth.module.css';

const ROLES = [
  { value: 'CONSUMER', label: 'Consumidor – Quiero comprar café' },
  { value: 'PRODUCER', label: 'Productor – Quiero vender mi café' },
];

export default function RegisterForm() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    mode: 'onChange', // Validación en tiempo real (RNF-009.2)
    defaultValues: { role: 'CONSUMER' },
  });

  const onSubmit = async (data) => {
    setServerError('');
    setIsSubmitting(true);

    try {
      await registerUser(data.name, data.email, data.password, data.role);
      navigate('/catalog');
    } catch (err) {
      const apiError = err?.response?.data?.error;
      if (apiError?.code === 'EMAIL_ALREADY_EXISTS') {
        setServerError('Este correo electrónico ya está registrado.');
      } else if (apiError?.message) {
        setServerError(apiError.message);
      } else {
        setServerError('Ocurrió un error al registrarte. Intenta nuevamente.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.formContainer}>
      <h1 className={styles.title}>Crear cuenta</h1>
      <p className={styles.subtitle}>
        Únete a Conexión Cafetera y descubre el mejor café colombiano.
      </p>

      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        aria-label="Formulario de registro"
        className={styles.form}
      >
        {/* Nombre */}
        <div className={styles.fieldGroup}>
          <label htmlFor="name" className={styles.label}>
            Nombre completo <span aria-hidden="true">*</span>
          </label>
          <input
            id="name"
            type="text"
            autoComplete="name"
            aria-required="true"
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? 'name-error' : undefined}
            className={`${styles.input} ${errors.name ? styles.inputError : ''}`}
            {...register('name', {
              required: 'El nombre es obligatorio.',
              minLength: { value: 2, message: 'El nombre debe tener al menos 2 caracteres.' },
              maxLength: { value: 100, message: 'El nombre no puede superar 100 caracteres.' },
            })}
          />
          {errors.name && (
            <p id="name-error" role="alert" className={styles.errorMessage}>
              {errors.name.message}
            </p>
          )}
        </div>

        {/* Correo electrónico */}
        <div className={styles.fieldGroup}>
          <label htmlFor="email" className={styles.label}>
            Correo electrónico <span aria-hidden="true">*</span>
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            aria-required="true"
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? 'email-error' : undefined}
            className={`${styles.input} ${errors.email ? styles.inputError : ''}`}
            {...register('email', {
              required: 'El correo electrónico es obligatorio.',
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Ingresa un correo electrónico válido.',
              },
            })}
          />
          {errors.email && (
            <p id="email-error" role="alert" className={styles.errorMessage}>
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Contraseña */}
        <div className={styles.fieldGroup}>
          <label htmlFor="password" className={styles.label}>
            Contraseña <span aria-hidden="true">*</span>
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            aria-required="true"
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? 'password-error' : 'password-hint'}
            className={`${styles.input} ${errors.password ? styles.inputError : ''}`}
            {...register('password', {
              required: 'La contraseña es obligatoria.',
              minLength: {
                value: 8,
                message: 'La contraseña debe tener al menos 8 caracteres.',
              },
            })}
          />
          {errors.password ? (
            <p id="password-error" role="alert" className={styles.errorMessage}>
              {errors.password.message}
            </p>
          ) : (
            <p id="password-hint" className={styles.hint}>
              Mínimo 8 caracteres.
            </p>
          )}
        </div>

        {/* Rol */}
        <div className={styles.fieldGroup}>
          <fieldset className={styles.fieldset}>
            <legend className={styles.legend}>
              ¿Cómo quieres usar la plataforma? <span aria-hidden="true">*</span>
            </legend>
            <div className={styles.radioGroup}>
              {ROLES.map(({ value, label }) => (
                <label key={value} className={styles.radioLabel}>
                  <input
                    type="radio"
                    value={value}
                    className={styles.radioInput}
                    {...register('role', { required: 'Selecciona un rol.' })}
                  />
                  {label}
                </label>
              ))}
            </div>
            {errors.role && (
              <p role="alert" className={styles.errorMessage}>
                {errors.role.message}
              </p>
            )}
          </fieldset>
        </div>

        {/* Error del servidor */}
        {serverError && (
          <div role="alert" className={styles.serverError}>
            {serverError}
          </div>
        )}

        {/* Botón de envío */}
        <button
          type="submit"
          disabled={isSubmitting}
          className={styles.submitButton}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Creando cuenta…' : 'Crear cuenta'}
        </button>
      </form>

      <p className={styles.footerText}>
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className={styles.link}>
          Inicia sesión
        </Link>
      </p>
    </div>
  );
}
