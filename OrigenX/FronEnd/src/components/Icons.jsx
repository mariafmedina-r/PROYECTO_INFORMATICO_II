/**
 * Icons.jsx – Biblioteca de íconos SVG profesionales.
 *
 * Uso: <Icon name="mapPin" size={16} className={styles.icon} />
 *
 * Todos los íconos son inline SVG, accesibles (aria-hidden por defecto),
 * escalables y sin dependencias externas.
 */

const defaultProps = {
  size: 20,
  color: 'currentColor',
  'aria-hidden': true,
  focusable: false,
};

function Svg({ size, color, children, ...rest }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...rest}
    >
      {children}
    </svg>
  );
}

/* ── Íconos individuales ─────────────────────────────────── */

export function MapPinIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z" />
      <circle cx="12" cy="10" r="3" />
    </Svg>
  );
}

export function ShoppingCartIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <circle cx="8" cy="21" r="1" />
      <circle cx="19" cy="21" r="1" />
      <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
    </Svg>
  );
}

export function AlertTriangleIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </Svg>
  );
}

export function SearchIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </Svg>
  );
}

export function LeafIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
      <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
    </Svg>
  );
}

export function CoffeeIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
      <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
      <line x1="6" x2="6" y1="2" y2="4" />
      <line x1="10" x2="10" y1="2" y2="4" />
      <line x1="14" x2="14" y1="2" y2="4" />
    </Svg>
  );
}

export function LockIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </Svg>
  );
}

export function PackageIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="m7.5 4.27 9 5.15" />
      <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
      <path d="m3.3 7 8.7 5 8.7-5" />
      <path d="M12 22V12" />
    </Svg>
  );
}

export function BellIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </Svg>
  );
}

export function CheckCircleIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <path d="m9 11 3 3L22 4" />
    </Svg>
  );
}

export function XCircleIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <circle cx="12" cy="12" r="10" />
      <path d="m15 9-6 6" />
      <path d="m9 9 6 6" />
    </Svg>
  );
}

export function UserIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </Svg>
  );
}

export function LogOutIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" x2="9" y1="12" y2="12" />
    </Svg>
  );
}

export function LogInIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
      <polyline points="10 17 15 12 10 7" />
      <line x1="15" x2="3" y1="12" y2="12" />
    </Svg>
  );
}

export function UserPlusIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <line x1="19" x2="19" y1="8" y2="14" />
      <line x1="22" x2="16" y1="11" y2="11" />
    </Svg>
  );
}

export function LayoutDashboardIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <rect width="7" height="9" x="3" y="3" rx="1" />
      <rect width="7" height="5" x="14" y="3" rx="1" />
      <rect width="7" height="9" x="14" y="12" rx="1" />
      <rect width="7" height="5" x="3" y="16" rx="1" />
    </Svg>
  );
}

export function StoreIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7" />
      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
      <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4" />
      <path d="M2 7h20" />
      <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7" />
    </Svg>
  );
}

export function FarmerIcon({ size = 20, color = 'currentColor', ...rest }) {
  // Representa al productor: persona con sombrero
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
      <path d="M8 7H4" />
      <path d="M20 7h-4" />
      <path d="M4 7c0-1 .5-2 2-2h12c1.5 0 2 1 2 2" />
    </Svg>
  );
}

export function ArrowRightIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M5 12h14" />
      <path d="m12 5 7 7-7 7" />
    </Svg>
  );
}

export function CheckIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M20 6 9 17l-5-5" />
    </Svg>
  );
}

export function XIcon({ size = 20, color = 'currentColor', ...rest }) {
  return (
    <Svg size={size} color={color} {...rest}>
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </Svg>
  );
}

/**
 * Componente genérico por nombre.
 * Uso: <Icon name="mapPin" size={16} />
 */
const ICON_MAP = {
  mapPin:        MapPinIcon,
  cart:          ShoppingCartIcon,
  alert:         AlertTriangleIcon,
  search:        SearchIcon,
  leaf:          LeafIcon,
  coffee:        CoffeeIcon,
  lock:          LockIcon,
  package:       PackageIcon,
  bell:          BellIcon,
  checkCircle:   CheckCircleIcon,
  xCircle:       XCircleIcon,
  user:          UserIcon,
  logOut:        LogOutIcon,
  logIn:         LogInIcon,
  userPlus:      UserPlusIcon,
  dashboard:     LayoutDashboardIcon,
  store:         StoreIcon,
  farmer:        FarmerIcon,
  arrowRight:    ArrowRightIcon,
  check:         CheckIcon,
  x:             XIcon,
};

export default function Icon({ name, size = 20, color = 'currentColor', ...rest }) {
  const Component = ICON_MAP[name];
  if (!Component) return null;
  return <Component size={size} color={color} aria-hidden {...rest} />;
}
