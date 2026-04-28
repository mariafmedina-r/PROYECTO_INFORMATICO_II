/**
 * AuthModule.jsx – Módulo de autenticación.
 *
 * Tarea 2.9 – Requerimientos: 1.1, 2.1, 2.4, 12.5, RNF-002.5, RNF-009.2
 *
 * Exporta las páginas de registro, login y recuperación de contraseña.
 * Cada página envuelve el formulario correspondiente en el layout de auth.
 */

import ForgotPasswordForm from './components/ForgotPasswordForm';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import styles from './auth.module.css';

/**
 * Página de inicio de sesión.
 */
export function LoginPage() {
  return (
    <main className={styles.authPage}>
      <LoginForm />
    </main>
  );
}

/**
 * Página de registro.
 */
export function RegisterPage() {
  return (
    <main className={styles.authPage}>
      <RegisterForm />
    </main>
  );
}

/**
 * Página de recuperación de contraseña.
 */
export function ForgotPasswordPage() {
  return (
    <main className={styles.authPage}>
      <ForgotPasswordForm />
    </main>
  );
}

// Exportación por defecto: LoginPage (compatibilidad con import default)
export default LoginPage;
