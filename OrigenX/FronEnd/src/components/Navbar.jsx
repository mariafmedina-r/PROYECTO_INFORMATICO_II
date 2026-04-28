/**
 * components/Navbar.jsx – Barra de navegación principal.
 *
 * Tarea 15 – RNF-008.1
 * También: Tareas 13.1, 14.2 – Requerimientos: 12.4, 19.2
 *
 * Muestra:
 *   - Logo / nombre de la marca
 *   - Enlace al catálogo
 *   - Ícono del carrito con badge de cantidad de ítems (Req. 12.4)
 *   - Campana de notificaciones con badge de no leídas (Req. 19.2)
 *   - Nombre y rol del usuario autenticado
 *   - Enlace al perfil / cerrar sesión si está autenticado
 *   - Enlace a login / registro si no está autenticado
 *   - Menú hamburguesa en móvil (< 768px)
 *
 * WCAG 2.1 AA:
 *   - Área mínima de toque 44×44 px (RNF-002.2)
 *   - Navegación por teclado: TAB, ENTER, ESC (RNF-002.4)
 *   - Contraste adecuado sobre fondo verde oscuro (RNF-002.1)
 *   - ARIA labels y roles semánticos
 */

import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { BellIcon, LayoutDashboardIcon, LogInIcon, LogOutIcon, PackageIcon, ShoppingCartIcon, StoreIcon, UserIcon, UserPlusIcon } from './Icons';
import styles from './Navbar.module.css';

/**
 * Campana de notificaciones con dropdown.
 * Importación dinámica para evitar errores si el módulo de órdenes no está disponible.
 */
function NotificationBell() {
  const [NotificationBellInner, setNotificationBellInner] = useState(null);

  useEffect(() => {
    // Importación dinámica para evitar errores si el módulo no existe aún
    import('../modules/orders/hooks/useNotifications')
      .then((mod) => {
        const { useNotifications } = mod;
        // Componente interno que usa el hook
        function Inner() {
          const { notifications = [], unreadCount = 0, markAsRead } = useNotifications();
          const [open, setOpen] = useState(false);
          const bellRef = useRef(null);

          useEffect(() => {
            if (!open) return;
            const handleClickOutside = (e) => {
              if (bellRef.current && !bellRef.current.contains(e.target)) {
                setOpen(false);
              }
            };
            const handleKeyDown = (e) => {
              if (e.key === 'Escape') setOpen(false);
            };
            document.addEventListener('mousedown', handleClickOutside);
            document.addEventListener('keydown', handleKeyDown);
            return () => {
              document.removeEventListener('mousedown', handleClickOutside);
              document.removeEventListener('keydown', handleKeyDown);
            };
          }, [open]);

          const recentNotifications = notifications.slice(0, 10);

          return (
            <div style={{ position: 'relative' }} ref={bellRef}>
              <button
                type="button"
                onClick={() => setOpen((prev) => !prev)}
                aria-label={
                  unreadCount > 0
                    ? `Notificaciones, ${unreadCount} sin leer`
                    : 'Notificaciones'
                }
                aria-expanded={open}
                aria-haspopup="true"
                style={{
                  position: 'relative',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '40px',
                  height: '40px',
                  background: 'rgba(255,255,255,0.12)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '10px',
                  color: '#ffffff',
                  cursor: 'pointer',
                  transition: 'background-color 150ms ease-in-out',
                  flexShrink: 0,
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
                  <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
                </svg>
                {unreadCount > 0 && (
                  <span
                    aria-hidden="true"
                    style={{
                      position: 'absolute',
                      top: '2px',
                      right: '2px',
                      minWidth: '18px',
                      height: '18px',
                      padding: '0 4px',
                      backgroundColor: 'var(--color-accent)',
                      color: '#ffffff',
                      fontSize: '0.6875rem',
                      fontWeight: '700',
                      borderRadius: '9999px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      lineHeight: '1',
                      pointerEvents: 'none',
                    }}
                  >
                    {unreadCount > 99 ? '99+' : unreadCount}
                  </span>
                )}
              </button>

              {open && (
                <div
                  role="dialog"
                  aria-label="Notificaciones recientes"
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 8px)',
                    right: 0,
                    width: '320px',
                    maxHeight: '400px',
                    overflowY: 'auto',
                    backgroundColor: 'var(--color-surface)',
                    borderRadius: 'var(--border-radius-lg)',
                    boxShadow: 'var(--shadow-lg)',
                    zIndex: 'var(--z-dropdown)',
                    border: '1px solid rgba(0,0,0,0.08)',
                  }}
                >
                  <div
                    style={{
                      padding: '12px 16px',
                      fontWeight: '600',
                      fontSize: '1rem',
                      color: 'var(--color-text-primary)',
                      borderBottom: '1px solid #e5e7eb',
                    }}
                  >
                    Notificaciones
                  </div>
                  <div>
                    {recentNotifications.length === 0 ? (
                      <p
                        style={{
                          padding: '16px',
                          color: 'var(--color-text-secondary)',
                          fontSize: '0.875rem',
                          textAlign: 'center',
                        }}
                      >
                        No tienes notificaciones.
                      </p>
                    ) : (
                      recentNotifications.map((notif) => (
                        <Link
                          key={notif.id}
                          to={notif.orderId ? `/orders/${notif.orderId}` : '/orders'}
                          onClick={async () => {
                            if (!notif.read && markAsRead) await markAsRead(notif.id);
                            setOpen(false);
                          }}
                          aria-label={`${notif.read ? '' : 'No leída: '}${notif.message}`}
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '4px',
                            padding: '12px 16px',
                            borderBottom: '1px solid #f3f4f6',
                            textDecoration: 'none',
                            backgroundColor: notif.read ? 'transparent' : 'rgba(65,122,61,0.06)',
                            transition: 'background-color 150ms',
                          }}
                        >
                          <span
                            style={{
                              fontSize: '0.875rem',
                              color: 'var(--color-text-primary)',
                              lineHeight: '1.4',
                            }}
                          >
                            {notif.message}
                          </span>
                          {notif.createdAt && (
                            <span
                              style={{
                                fontSize: '0.75rem',
                                color: 'var(--color-text-secondary)',
                              }}
                            >
                              {new Date(notif.createdAt?.toDate?.() ?? notif.createdAt).toLocaleDateString('es-CO', {
                                month: 'short',
                                day: 'numeric',
                              })}
                            </span>
                          )}
                        </Link>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        }
        setNotificationBellInner(() => Inner);
      })
      .catch(() => {
        // El módulo de notificaciones no está disponible aún
        setNotificationBellInner(null);
      });
  }, []);

  if (!NotificationBellInner) return null;
  return <NotificationBellInner />;
}

/** Etiqueta legible del rol */
function getRoleLabel(role) {
  switch (role) {
    case 'CONSUMER': return 'Consumidor';
    case 'PRODUCER': return 'Productor';
    case 'ADMIN': return 'Admin';
    default: return role;
  }
}

export default function Navbar() {
  const { isAuthenticated, isConsumer, isProducer, currentUser, userRole, producerFarmName, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Cerrar menú al hacer clic fuera
  useEffect(() => {
    if (!menuOpen) return;
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  // Cerrar menú con ESC (RNF-002.4)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && menuOpen) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [menuOpen]);

  // Cerrar menú al cambiar de ruta
  const closeMenu = () => setMenuOpen(false);

  const handleLogout = async () => {
    closeMenu();
    await logout();
    navigate('/login', { replace: true });
  };

  const userName = isProducer
    ? (producerFarmName || currentUser?.displayName || currentUser?.email || '')
    : (currentUser?.displayName || currentUser?.email || '');

  return (
    <header ref={menuRef}>
      <nav className={styles.navbar} aria-label="Navegación principal">
        <div className={styles.navInner}>
          {/* Logo + info de usuario autenticado */}
          <div className={styles.navLogoGroup}>
            <Link
              to="/origen"
              className={styles.navLogo}
              aria-label="Conexión Cafetera – Ir al inicio"
              onClick={closeMenu}
            >
              Conexión Cafetera
            </Link>

            {/* Pill de usuario + rol */}
            {isAuthenticated && userName && (
              <div className={styles.userPills} aria-label={`Usuario: ${userName}`}>
                <span className={styles.userNamePill}>
                  {/* Ícono de usuario SVG */}
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
                    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  {userName.split(' ')[0]}
                </span>
                {userRole && (
                  <span className={`${styles.userRolePill} ${styles[`userRolePill_${userRole}`]}`}>
                    {getRoleLabel(userRole)}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Links de navegación centrados */}
          <nav className={styles.navCenter} aria-label="Navegación principal">
            <NavLink
              to="/origen"
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
              }
            >
              Origen
            </NavLink>
            <NavLink
              to="/productores"
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
              }
            >
              Productores
            </NavLink>
            <NavLink
              to="/catalog"
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
              }
            >
              Catálogo
            </NavLink>

            {/* Mis pedidos (CONSUMER) – junto a los links de navegación */}
            {isAuthenticated && isConsumer && (
              <NavLink
                to="/orders"
                className={({ isActive }) =>
                  `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
                }
              >
                Mis pedidos
              </NavLink>
            )}

            {/* Mi perfil (CONSUMER) */}
            {isAuthenticated && isConsumer && (
              <NavLink
                to="/profile"
                className={({ isActive }) =>
                  `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
                }
              >
                Mi perfil
              </NavLink>
            )}

            {/* Panel del productor (PRODUCER) – junto a los links principales */}
            {isAuthenticated && isProducer && (
              <NavLink
                to="/producer"
                className={({ isActive }) =>
                  `${styles.navLinkProducer} ${isActive ? styles.navLinkProducerActive : ''}`
                }
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
                  <rect width="7" height="9" x="3" y="3" rx="1" />
                  <rect width="7" height="5" x="14" y="3" rx="1" />
                  <rect width="7" height="9" x="14" y="12" rx="1" />
                  <rect width="7" height="5" x="3" y="16" rx="1" />
                </svg>
                Mi panel
              </NavLink>
            )}
          </nav>

          {/* Acciones de usuario (derecha) */}
          <div className={styles.navRight}>
            <div className={styles.navLinks} role="list">

              {/* Carrito con badge (Req. 12.4, RNF-008.1) */}
              {isAuthenticated && isConsumer && (
                <Link
                  to="/cart"
                  className={styles.navCartButton}
                  aria-label={
                    itemCount > 0
                      ? `Carrito, ${itemCount} ítem${itemCount !== 1 ? 's' : ''}`
                      : 'Carrito vacío'
                  }
                  role="listitem"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/>
                    <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>
                  </svg>
                  {itemCount > 0 && (
                    <span className={styles.navCartBadge} aria-hidden="true">
                      {itemCount > 99 ? '99+' : itemCount}
                    </span>
                  )}
                </Link>
              )}

              {/* Campana de notificaciones (CONSUMER) */}
              {isAuthenticated && isConsumer && (
                <div role="listitem">
                  <NotificationBell />
                </div>
              )}

              {/* Autenticado: cerrar sesión */}
              {isAuthenticated ? (
                <button
                  type="button"
                  onClick={handleLogout}
                  className={styles.navButton}
                  role="listitem"
                >
                  Cerrar sesión
                </button>
              ) : (
                <>
                  <NavLink
                    to="/login"
                    className={({ isActive }) =>
                      `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
                    }
                    role="listitem"
                  >
                    Iniciar sesión
                  </NavLink>
                  <NavLink
                    to="/register"
                    className={({ isActive }) =>
                      `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
                    }
                    role="listitem"
                  >
                    Registrarse
                  </NavLink>
                </>
              )}
            </div>

            {/* Botón hamburguesa (móvil) */}
            <button
              type="button"
              className={`${styles.hamburger} ${menuOpen ? styles.hamburgerOpen : ''}`}
              onClick={() => setMenuOpen((prev) => !prev)}
              aria-label={menuOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'}
              aria-expanded={menuOpen}
              aria-controls="mobile-menu"
            >
              <span className={styles.hamburgerLine} aria-hidden="true" />
              <span className={styles.hamburgerLine} aria-hidden="true" />
              <span className={styles.hamburgerLine} aria-hidden="true" />
            </button>
          </div>
        </div>
      </nav>

      {/* Menú móvil */}
      <div
        id="mobile-menu"
        className={`${styles.mobileMenu} ${menuOpen ? styles.mobileMenuOpen : ''}`}
        role="navigation"
        aria-label="Menú de navegación móvil"
        aria-hidden={!menuOpen}
      >
        {/* Origen */}
        <NavLink
          to="/origen"
          className={({ isActive }) =>
            `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
          }
          onClick={closeMenu}
        >
          🌿 Origen
        </NavLink>

        {/* Productores */}
        <NavLink
          to="/productores"
          className={({ isActive }) =>
            `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
          }
          onClick={closeMenu}
        >
          👨‍🌾 Productores
        </NavLink>

        {/* Catálogo */}
        <NavLink
          to="/catalog"
          className={({ isActive }) =>
            `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
          }
          onClick={closeMenu}
        >
          🏪 Catálogo
        </NavLink>

        {/* Carrito (CONSUMER) */}
        {isAuthenticated && isConsumer && (
          <NavLink
            to="/cart"
            className={({ isActive }) =>
              `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
            }
            onClick={closeMenu}
            aria-label={
              itemCount > 0
                ? `Carrito, ${itemCount} ítem${itemCount !== 1 ? 's' : ''}`
                : 'Carrito vacío'
            }
          >
            🛒 Carrito
            {itemCount > 0 && (
              <span className={styles.mobileCartBadge} aria-hidden="true">
                {itemCount > 99 ? '99+' : itemCount}
              </span>
            )}
          </NavLink>
        )}

        {/* Mis pedidos (CONSUMER) */}
        {isAuthenticated && isConsumer && (
          <NavLink
            to="/orders"
            className={({ isActive }) =>
              `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
            }
            onClick={closeMenu}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>
            </svg>
            Mis pedidos
          </NavLink>
        )}

        {/* Mi perfil (CONSUMER) */}
        {isAuthenticated && isConsumer && (
          <NavLink
            to="/profile"
            className={({ isActive }) =>
              `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
            }
            onClick={closeMenu}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            Mi perfil
          </NavLink>
        )}

        {/* Panel del productor (PRODUCER) */}
        {isAuthenticated && isProducer && (
          <NavLink
            to="/producer"
            className={({ isActive }) =>
              `${styles.mobileNavLinkProducer} ${isActive ? styles.mobileNavLinkProducerActive : ''}`
            }
            onClick={closeMenu}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
              <rect width="7" height="9" x="3" y="3" rx="1" />
              <rect width="7" height="5" x="14" y="3" rx="1" />
              <rect width="7" height="9" x="14" y="12" rx="1" />
              <rect width="7" height="5" x="3" y="16" rx="1" />
            </svg>
            Mi panel
          </NavLink>
        )}

        <hr className={styles.mobileDivider} />

        {/* Autenticado: info + cerrar sesión */}
        {isAuthenticated ? (
          <>
            {userName && (
              <span
                className={styles.mobileNavLink}
                style={{ cursor: 'default', opacity: 0.75, fontSize: '0.875rem' }}
                aria-label={`Usuario: ${userName}`}
              >
                👤 {userName}
                {userRole && (
                  <span
                    style={{
                      marginLeft: '8px',
                      padding: '2px 8px',
                      backgroundColor: 'rgba(255,255,255,0.15)',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                    }}
                  >
                    {getRoleLabel(userRole)}
                  </span>
                )}
              </span>
            )}
            <button
              type="button"
              onClick={handleLogout}
              className={styles.mobileNavButton}
            >
              🚪 Cerrar sesión
            </button>
          </>
        ) : (
          <>
            <NavLink
              to="/login"
              className={({ isActive }) =>
                `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
              }
              onClick={closeMenu}
            >
              🔑 Iniciar sesión
            </NavLink>
            <NavLink
              to="/register"
              className={({ isActive }) =>
                `${styles.mobileNavLink} ${isActive ? styles.mobileNavLinkActive : ''}`
              }
              onClick={closeMenu}
            >
              ✍️ Registrarse
            </NavLink>
          </>
        )}
      </div>
    </header>
  );
}
