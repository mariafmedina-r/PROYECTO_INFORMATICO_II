/**
 * components/LoginForm.jsx – Formulario de inicio de sesión.
 *
 * Tarea 2.9 – Requerimientos: 2.1, 2.2, RNF-002.5, RNF-009.2
 *
 * Usa react-hook-form para validación en tiempo real.
 * Muestra mensajes de error genéricos para no revelar información (Req. 2.2).
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import styles from '../auth.module.css';

export default function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirigir a la ruta de origen tras el login (Req. 12.5)
  const from = location.state?.from?.pathname || '/catalog';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    mode: 'onChange', // Validación en tiempo real (RNF-009.2)
  });

  const onSubmit = async (data) => {
    setServerError('');
    setIsSubmitting(true);

    try {
      await login(data.email, data.password);
      // Redirigir a la ruta de origen si venía de una ruta protegida,
      // o a /auth/redirect para que decida según el rol
      if (location.state?.from?.pathname) {
        navigate(location.state.from.pathname, { replace: true });
      } else {
        navigate('/auth/redirect', { replace: true });
      }
    } catch (err) {
      // Mensaje genérico sin revelar cuál campo es incorrecto (Req. 2.2)
      const firebaseCode = err?.code;
      if (
        firebaseCode === 'auth/too-many-requests' ||
        err?.response?.status === 429
      ) {
        setServerError(
          'Demasiados intentos fallidos. Espera unos minutos antes de intentarlo nuevamente.',
        );
      } else {
        setServerError(
          'Credenciales inválidas. Verifica tu correo y contraseña.',
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.formContainer}>
      <h1 className={styles.title}>Iniciar sesión</h1>
      <p className={styles.subtitle}>
        Bienvenido de vuelta a Conexión Cafetera.
      </p>

      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        aria-label="Formulario de inicio de sesión"
        className={styles.form}
      >
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
            autoComplete="current-password"
            aria-required="true"
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? 'password-error' : undefined}
            className={`${styles.input} ${errors.password ? styles.inputError : ''}`}
            {...register('password', {
              required: 'La contraseña es obligatoria.',
            })}
          />
          {errors.password && (
            <p id="password-error" role="alert" className={styles.errorMessage}>
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Enlace de recuperación */}
        <div className={styles.forgotPasswordRow}>
          <Link to="/forgot-password" className={styles.link}>
            ¿Olvidaste tu contraseña?
          </Link>
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
          {isSubmitting ? 'Iniciando sesión…' : 'Iniciar sesión'}
        </button>
      </form>

      <p className={styles.footerText}>
        ¿No tienes cuenta?{' '}
        <Link to="/register" className={styles.link}>
          Regístrate
        </Link>
      </p>
    </div>
  );
}
