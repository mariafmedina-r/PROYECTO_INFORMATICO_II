/**
 * components/ForgotPasswordForm.jsx – Formulario de recuperación de contraseña.
 *
 * Tarea 2.9 – Requerimientos: 2.4, 2.5, RNF-002.5, RNF-009.2
 *
 * Siempre muestra el mismo mensaje de confirmación, sin revelar si el correo
 * está registrado (Req. 2.5).
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import styles from '../auth.module.css';

export default function ForgotPasswordForm() {
  const { forgotPassword } = useAuth();
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    mode: 'onChange', // Validación en tiempo real (RNF-009.2)
  });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await forgotPassword(data.email);
    } finally {
      // Siempre mostrar el mensaje de confirmación, sin revelar si el correo existe (Req. 2.5)
      setIsSubmitting(false);
      setSubmitted(true);
    }
  };

  if (submitted) {
    return (
      <div className={styles.formContainer}>
        <h1 className={styles.title}>Revisa tu correo</h1>
        <p className={styles.subtitle}>
          Si el correo está registrado, recibirás un enlace de restablecimiento
          en los próximos minutos. Revisa también tu carpeta de spam.
        </p>
        <Link to="/login" className={styles.submitButton} style={{ textAlign: 'center', display: 'block' }}>
          Volver al inicio de sesión
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.formContainer}>
      <h1 className={styles.title}>Recuperar contraseña</h1>
      <p className={styles.subtitle}>
        Ingresa tu correo electrónico y te enviaremos un enlace para restablecer
        tu contraseña.
      </p>

      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        aria-label="Formulario de recuperación de contraseña"
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

        {/* Botón de envío */}
        <button
          type="submit"
          disabled={isSubmitting}
          className={styles.submitButton}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Enviando…' : 'Enviar enlace de recuperación'}
        </button>
      </form>

      <p className={styles.footerText}>
        <Link to="/login" className={styles.link}>
          ← Volver al inicio de sesión
        </Link>
      </p>
    </div>
  );
}
