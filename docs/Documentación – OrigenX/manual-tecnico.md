# 🛠️ Manual Técnico – OrigenX / Conexión Cafetera

**MFRAL TECH** · Universidad Autónoma de Occidente · 2026

---

## Tabla de contenido

1. [Requisitos del sistema](#1-requisitos-del-sistema)
2. [Estructura del proyecto](#2-estructura-del-proyecto)
3. [Configuración del Backend](#3-configuración-del-backend)
4. [Configuración del Frontend](#4-configuración-del-frontend)
5. [Ejecución en desarrollo](#5-ejecución-en-desarrollo)
6. [Ejecución en producción](#6-ejecución-en-producción)
7. [Variables de entorno](#7-variables-de-entorno)
8. [Firebase – configuración](#8-firebase--configuración)
9. [Pruebas](#9-pruebas)
10. [Despliegue](#10-despliegue)

---

## 1. Requisitos del sistema

### Software requerido

| Herramienta | Versión mínima | Uso |
|-------------|---------------|-----|
| Python | 3.12+ | Runtime del backend |
| Node.js | 18+ | Runtime del frontend |
| npm | 9+ | Gestor de paquetes frontend |
| pip | 23+ | Gestor de paquetes Python |
| Git | 2.x | Control de versiones |
| ngrok | 3.x | Túnel HTTPS para exponer el backend |

### Cuentas y servicios externos

- Cuenta Google con acceso al proyecto Firebase `origenx-f3d66`
- Archivo `firebase-service-account.json` (credenciales del servidor — **nunca subir al repositorio**)

---

## 2. Estructura del proyecto

```
Proyecto Alternativo/
├── doc/                          ← Documentación del proyecto
│   ├── README.md
│   ├── manual-tecnico.md
│   ├── manual-usuario.md
│   ├── procedimientos.md
│   └── arquitectura.md
└── OrigenX/
    ├── BackEnd/                  ← API REST (FastAPI + Python)
    │   ├── main.py               ← Punto de entrada de la aplicación
    │   ├── requirements.txt      ← Dependencias Python
    │   ├── firebase_config.py    ← Inicialización Firebase Admin SDK
    │   ├── .env                  ← Variables de entorno (NO subir)
    │   ├── .env.example          ← Plantilla de variables de entorno
    │   ├── firebase-service-account.json  ← Credenciales (NO subir)
    │   ├── middleware/           ← Autenticación y rate limiting
    │   │   ├── auth_middleware.py
    │   │   └── rate_limit.py
    │   ├── models/               ← Esquemas Pydantic
    │   │   ├── user.py
    │   │   ├── product.py
    │   │   ├── order.py
    │   │   ├── cart.py
    │   │   ├── payment.py
    │   │   ├── producer.py
    │   │   └── address.py
    │   ├── repositories/         ← Acceso a Firestore
    │   │   ├── user_repository.py
    │   │   ├── product_repository.py
    │   │   ├── order_repository.py
    │   │   ├── cart_repository.py
    │   │   ├── producer_repository.py
    │   │   ├── address_repository.py
    │   │   └── notification_repository.py
    │   ├── services/             ← Lógica de negocio
    │   │   ├── auth_service.py
    │   │   ├── product_service.py
    │   │   ├── order_service.py
    │   │   ├── cart_service.py
    │   │   ├── payment_service.py
    │   │   ├── producer_service.py
    │   │   ├── shipping_service.py
    │   │   ├── address_service.py
    │   │   └── notification_service.py
    │   ├── routes/               ← Controladores HTTP
    │   │   ├── auth.py
    │   │   ├── products.py
    │   │   ├── producers.py
    │   │   ├── orders.py
    │   │   ├── cart.py
    │   │   ├── payments.py
    │   │   ├── shipping.py
    │   │   ├── sales.py
    │   │   └── addresses.py
    │   └── tests/                ← Pruebas unitarias e integración
    └── FronEnd/                  ← SPA React + Vite
        ├── index.html
        ├── package.json
        ├── vite.config.js
        ├── .env                  ← Variables de entorno (NO subir)
        └── src/
            ├── main.jsx          ← Punto de entrada React
            ├── App.jsx           ← Rutas principales
            ├── config/
            │   ├── firebase.js   ← Firebase Client SDK
            │   └── axios.js      ← Cliente HTTP con interceptores
            ├── context/
            │   ├── AuthContext.jsx   ← Estado global de autenticación
            │   ├── CartContext.jsx   ← Estado global del carrito
            │   └── ToastContext.jsx  ← Notificaciones UI
            ├── components/       ← Componentes reutilizables
            └── modules/          ← Módulos por funcionalidad
                ├── auth/
                ├── catalog/
                ├── cart/
                ├── checkout/
                ├── orders/
                ├── producer/
                ├── productores/
                ├── profile/
                └── origen/
```

---

## 3. Configuración del Backend

### 3.1 Clonar y preparar entorno

```bash
# Navegar a la carpeta del backend
cd OrigenX/BackEnd

# Crear entorno virtual Python
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3.2 Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.example .env
```

Editar `.env` con los valores reales:

```env
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
FIREBASE_PROJECT_ID=origenx-f3d66
FIREBASE_STORAGE_BUCKET=origenx-f3d66.firebasestorage.app
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
AUTH_MAX_FAILED_ATTEMPTS=5
AUTH_LOCKOUT_MINUTES=15
```

### 3.3 Colocar credenciales Firebase

Descargar `firebase-service-account.json` desde:
> Firebase Console → Configuración del proyecto → Cuentas de servicio → Generar nueva clave privada

Colocar el archivo en `OrigenX/BackEnd/firebase-service-account.json`

> ⚠️ **Este archivo NUNCA debe subirse al repositorio.** Está en `.gitignore`.

---

## 4. Configuración del Frontend

### 4.1 Instalar dependencias

```bash
cd OrigenX/FronEnd
npm install
```

### 4.2 Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=origenx-f3d66.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=origenx-f3d66
VITE_FIREBASE_STORAGE_BUCKET=origenx-f3d66.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=438574650832
VITE_FIREBASE_APP_ID=1:438574650832:web:...

# URL del backend (local o producción)
VITE_API_BASE_URL=http://localhost:8000
```

---

## 5. Ejecución en desarrollo

### Backend

```bash
cd OrigenX/BackEnd
.venv\Scripts\activate          # Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor queda disponible en:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend

```bash
cd OrigenX/FronEnd
npm run dev
```

La aplicación queda disponible en: `http://localhost:5173`

> El frontend se comunica con el backend a través de la variable `VITE_API_BASE_URL`.

---

## 6. Ejecución en producción

### Backend (servidor con IP pública)

```bash
cd OrigenX/BackEnd
.venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

Para ejecutar como servicio en segundo plano (Linux):

```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > backend.log 2>&1 &
```

### Frontend (servidor local o propio)

```bash
cd OrigenX/FronEnd

# Compilar para producción
npm run build

# Servir el build (opcional, para pruebas locales)
npm run preview
```

Los archivos compilados quedan en `dist/` y pueden servirse desde cualquier servidor web (Nginx, Apache, etc.).

URL local de preview: **http://localhost:4173**

---

## 7. Variables de entorno

### Backend (`.env`)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `FIREBASE_CREDENTIALS_PATH` | Ruta al JSON de credenciales | `./firebase-service-account.json` |
| `FIREBASE_PROJECT_ID` | ID del proyecto Firebase | `origenx-f3d66` |
| `FIREBASE_STORAGE_BUCKET` | Bucket de Storage | `origenx-f3d66.firebasestorage.app` |
| `APP_ENV` | Entorno de ejecución | `development` / `production` |
| `APP_HOST` | Host del servidor | `0.0.0.0` |
| `APP_PORT` | Puerto del servidor | `8000` |
| `APP_DEBUG` | Modo debug (recarga automática) | `true` / `false` |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma) | `http://localhost:5173` |
| `AUTH_MAX_FAILED_ATTEMPTS` | Intentos fallidos antes de bloqueo | `5` |
| `AUTH_LOCKOUT_MINUTES` | Minutos de bloqueo tras intentos fallidos | `15` |

### Frontend (`.env`)

| Variable | Descripción |
|----------|-------------|
| `VITE_FIREBASE_API_KEY` | API Key del proyecto Firebase |
| `VITE_FIREBASE_AUTH_DOMAIN` | Dominio de autenticación Firebase |
| `VITE_FIREBASE_PROJECT_ID` | ID del proyecto Firebase |
| `VITE_FIREBASE_STORAGE_BUCKET` | Bucket de Firebase Storage |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | ID del remitente de mensajes |
| `VITE_FIREBASE_APP_ID` | ID de la aplicación Firebase |
| `VITE_API_BASE_URL` | URL base del backend FastAPI |

---

## 8. Firebase – configuración

### Servicios utilizados

| Servicio | Uso |
|----------|-----|
| Firebase Authentication | Registro, login, tokens JWT |
| Cloud Firestore | Base de datos NoSQL principal |
| Firebase Storage | Almacenamiento de imágenes de productos y perfiles |

### Colecciones Firestore

| Colección | Descripción |
|-----------|-------------|
| `users` | Datos de usuarios registrados |
| `products` | Productos del catálogo |
| `products/{id}/images` | Imágenes de cada producto |
| `producer_profiles` | Perfiles públicos de productores |
| `carts/{userId}/items` | Ítems del carrito por usuario |
| `orders` | Pedidos realizados |
| `orders/{id}/items` | Ítems de cada pedido |
| `addresses/{userId}/items` | Direcciones de envío por usuario |
| `notifications/{userId}/items` | Notificaciones por usuario |

---

## 9. Pruebas

### Ejecutar pruebas del backend

```bash
cd OrigenX/BackEnd
.venv\Scripts\activate

# Todas las pruebas
pytest

# Con reporte de cobertura
pytest --cov=. --cov-report=term-missing

# Prueba específica
pytest tests/test_auth_service.py -v
```

### Archivos de prueba disponibles

| Archivo | Módulo cubierto |
|---------|----------------|
| `test_auth_service.py` | Autenticación |
| `test_auth_routes.py` | Rutas de auth |
| `test_product_create.py` | Creación de productos |
| `test_product_update.py` | Actualización de productos |
| `test_product_status.py` | Estado de productos |
| `test_product_images.py` | Gestión de imágenes |
| `test_cart.py` | Carrito de compras |
| `test_order_history.py` | Historial de pedidos |
| `test_addresses.py` | Direcciones de envío |
| `test_sales.py` | Panel de ventas |
| `test_payment_service.py` | Servicio de pagos |
| `test_shipping_service.py` | Servicio de envíos |
| `test_notification_service.py` | Notificaciones |
| `test_producer_service.py` | Perfil de productor |
| `test_catalog.py` | Catálogo público |
| `test_models.py` | Modelos Pydantic |
| `test_rate_limiter.py` | Rate limiting |

---

## 10. Despliegue

### Flujo completo de despliegue

```
1. Hacer cambios en el código
2. Probar localmente (npm run dev / uvicorn --reload)
3. Ejecutar pruebas del backend (pytest)
4. Compilar frontend (npm run build)
5. Reiniciar backend en servidor de producción
```

### Comandos rápidos

```bash
# Frontend — build
cd OrigenX/FronEnd && npm run build

# Backend — reiniciar
pkill -f uvicorn && nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > backend.log 2>&1 &

# ngrok — exponer backend con HTTPS
ngrok http 8000
```

