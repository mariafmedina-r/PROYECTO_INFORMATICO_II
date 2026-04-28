# ⚙️ Manual de Procedimientos – Conexión Cafetera

**MFRAL TECH** · Universidad Autónoma de Occidente · 2026

---

## Tabla de contenido

1. [Procedimientos de autenticación](#1-procedimientos-de-autenticación)
2. [Procedimientos del consumidor](#2-procedimientos-del-consumidor)
3. [Procedimientos del productor](#3-procedimientos-del-productor)
4. [Flujos de estado de pedidos](#4-flujos-de-estado-de-pedidos)
5. [Procedimientos de gestión de stock](#5-procedimientos-de-gestión-de-stock)
6. [Procedimientos de seguridad](#6-procedimientos-de-seguridad)
7. [Procedimientos de administración del sistema](#7-procedimientos-de-administración-del-sistema)
8. [Manejo de errores y excepciones](#8-manejo-de-errores-y-excepciones)

---

## 1. Procedimientos de autenticación

### PRO-AUTH-001 — Registro de nuevo usuario

```
INICIO
  │
  ├─► El usuario accede a /register
  ├─► Selecciona rol: CONSUMER o PRODUCER
  ├─► Completa formulario (nombre, email, contraseña, confirmación)
  ├─► El frontend valida campos localmente
  │     ├─ Error → Muestra mensajes de validación inline
  │     └─ OK → Envía POST /api/auth/register
  ├─► El backend:
  │     ├─ Verifica que el email no esté registrado
  │     ├─ Crea usuario en Firebase Authentication
  │     ├─ Asigna Custom Claim de rol (CONSUMER / PRODUCER)
  │     └─ Crea documento en colección /users en Firestore
  ├─► El frontend hace signInWithEmailAndPassword automáticamente
  ├─► onAuthStateChanged detecta el nuevo usuario
  └─► Redirige según rol:
        ├─ CONSUMER → /catalog
        └─ PRODUCER → /producer
FIN
```

### PRO-AUTH-002 — Inicio de sesión

```
INICIO
  │
  ├─► El usuario accede a /login
  ├─► Ingresa email y contraseña
  ├─► El frontend llama signInWithEmailAndPassword (Firebase Auth)
  │     ├─ Error de credenciales → Muestra mensaje de error
  │     ├─ Cuenta bloqueada (5 intentos) → Muestra tiempo de espera
  │     └─ OK → Firebase retorna ID Token con Custom Claims
  ├─► onAuthStateChanged se dispara
  ├─► El frontend lee el rol del token (claims.role)
  ├─► Si rol = PRODUCER → Carga farmName desde /api/producers/{uid}
  ├─► Inicia timer de inactividad (5 minutos)
  └─► Redirige a la ruta de origen o a la solicitada antes del login
FIN
```

### PRO-AUTH-003 — Cierre de sesión por inactividad

```
INICIO
  │
  ├─► El sistema detecta 5 minutos sin actividad del usuario
  │     (sin mousemove, click, keydown, scroll, touchstart)
  ├─► Se ejecuta signOut(auth) automáticamente
  ├─► onAuthStateChanged detecta usuario null
  ├─► Se limpian todos los estados globales (carrito, rol, usuario)
  └─► El usuario es redirigido a /login
FIN
```

### PRO-AUTH-004 — Recuperación de contraseña

```
INICIO
  │
  ├─► El usuario hace clic en "¿Olvidaste tu contraseña?"
  ├─► Ingresa su correo electrónico
  ├─► El frontend llama sendPasswordResetEmail (Firebase Auth)
  │     ├─ Email no registrado → No se revela (respuesta genérica)
  │     └─ Email registrado → Firebase envía correo de recuperación
  └─► Se muestra mensaje: "Si el correo existe, recibirás instrucciones"
FIN
```

---

## 2. Procedimientos del consumidor

### PRO-CON-001 — Agregar producto al carrito

```
INICIO
  │
  ├─► El consumidor navega al catálogo o detalle de producto
  ├─► Selecciona cantidad deseada (máximo = stock disponible)
  ├─► Hace clic en "Agregar al carrito"
  │     ├─ No autenticado → Redirige a /login con estado de retorno
  │     ├─ Rol PRODUCER → Muestra aviso "Solo consumidores pueden comprar"
  │     └─ Autenticado CONSUMER → Envía POST /api/cart/items
  ├─► El backend:
  │     ├─ Verifica que el producto existe y está activo
  │     ├─ Verifica que hay stock suficiente
  │     └─ Agrega o actualiza ítem en /carts/{userId}/items
  └─► El frontend actualiza el badge del carrito en la navbar
FIN
```

### PRO-CON-002 — Proceso de checkout

```
INICIO
  │
  ├─► El consumidor accede al carrito (/cart)
  ├─► Revisa los productos y cantidades
  ├─► Hace clic en "Proceder al pago"
  │
  ├─► PASO 1: Dirección de envío
  │     ├─ Selecciona dirección existente, o
  │     └─ Crea nueva dirección → POST /api/addresses
  │
  ├─► PASO 2: Empresa de envío
  │     ├─ El frontend carga opciones desde GET /api/shipping
  │     └─ El consumidor selecciona una opción
  │
  ├─► PASO 3: Pago
  │     ├─ El consumidor ingresa datos de tarjeta
  │     └─ El frontend envía POST /api/payments/process
  │
  ├─► PASO 4: Creación del pedido
  │     ├─ El frontend envía POST /api/orders
  │     ├─ El backend:
  │     │     ├─ Valida carrito no vacío
  │     │     ├─ Valida dirección y empresa de envío
  │     │     ├─ Crea snapshot de productos (nombre, precio, cantidad)
  │     │     ├─ Crea documento en /orders con estado "pendiente"
  │     │     ├─ Crea ítems en /orders/{id}/items
  │     │     ├─ Vacía el carrito automáticamente
  │     │     └─ Descuenta stock de cada producto
  │     └─ El frontend muestra confirmación con número de pedido
FIN
```

### PRO-CON-003 — Consultar historial de pedidos

```
INICIO
  │
  ├─► El consumidor accede a /orders
  ├─► El frontend envía GET /api/orders
  ├─► El backend retorna pedidos del consumidor con:
  │     ├─ Datos del pedido (fecha, estado, total)
  │     └─ Preview de los primeros 3 ítems con imagen principal
  ├─► El consumidor hace clic en un pedido
  ├─► El frontend envía GET /api/orders/{id}
  └─► Se muestra detalle completo con fecha estimada de entrega
FIN
```

---

## 3. Procedimientos del productor

### PRO-PRO-001 — Crear producto

```
INICIO
  │
  ├─► El productor accede a /producer → pestaña "Mis Productos"
  ├─► Hace clic en "+ Nuevo Producto"
  ├─► Completa el formulario (nombre, descripción, precio, stock)
  ├─► Sube imágenes del producto (máximo 5)
  │     ├─ El frontend envía POST /api/products/{id}/images
  │     └─ Las imágenes se almacenan en Firebase Storage
  ├─► Hace clic en "Guardar"
  ├─► El frontend envía POST /api/products
  ├─► El backend:
  │     ├─ Valida campos obligatorios
  │     ├─ Asocia el producto al producerId del token
  │     └─ Crea documento en /products con status "active"
  └─► El producto aparece en la tabla y en el catálogo público
FIN
```

### PRO-PRO-002 — Gestionar estado de producto

```
INICIO
  │
  ├─► El productor hace clic en "Desactivar" o "Activar"
  ├─► El frontend envía PATCH /api/products/{id}/status
  ├─► El backend:
  │     ├─ Verifica que el producto pertenece al productor
  │     └─ Actualiza campo status: "active" | "inactive"
  ├─► Si status = "inactive":
  │     └─ El producto desaparece del catálogo público
  └─► Si status = "active":
        └─ El producto vuelve a aparecer en el catálogo
FIN
```

### PRO-PRO-003 — Consultar ventas

```
INICIO
  │
  ├─► El productor accede a /producer → pestaña "Mis Ventas"
  ├─► El frontend envía GET /api/sales
  ├─► El backend:
  │     ├─ Obtiene todos los pedidos que contienen productos del productor
  │     ├─ Filtra los ítems para mostrar solo los del productor
  │     ├─ Enriquece cada pedido con info del cliente (nombre, email)
  │     └─ Calcula totales del mes actual y mes anterior
  ├─► El productor puede filtrar por rango de fechas
  │     └─ GET /api/sales?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD
  └─► Se muestra tabla (desktop) o tarjetas (móvil) con la información
FIN
```

### PRO-PRO-004 — Actualizar estado de pedido

```
INICIO
  │
  ├─► El productor identifica un pedido en "Mis Ventas"
  ├─► Hace clic en el botón de cambio de estado
  ├─► El frontend envía PATCH /api/orders/{id}/status
  ├─► El backend:
  │     ├─ Verifica que el productor tiene productos en el pedido
  │     ├─ Valida que la transición de estado es válida:
  │     │     pagado → en_preparacion → enviado
  │     ├─ Actualiza el estado y registra timestamp
  │     └─ Envía notificación al consumidor
  └─► El consumidor recibe notificación en su campana 🔔
FIN
```

---

## 4. Flujos de estado de pedidos

### Máquina de estados

```
                    ┌─────────────┐
                    │  PENDIENTE  │
                    └──────┬──────┘
                           │ Pago confirmado
                    ┌──────▼──────┐
                    │    PAGADO   │◄──────────────────┐
                    └──────┬──────┘                   │
                           │ Productor procesa         │
               ┌───────────▼───────────┐              │
               │    EN PREPARACIÓN     │              │
               └───────────┬───────────┘              │
                           │ Productor envía           │
                    ┌──────▼──────┐                   │
                    │   ENVIADO   │                   │
                    └──────┬──────┘                   │
                           │ Entrega confirmada        │
                    ┌──────▼──────┐                   │
                    │  ENTREGADO  │                   │
                    └─────────────┘                   │
                                                      │
         PENDIENTE ──────────────────────────► CANCELADO
         PAGADO ─────────────────────────────► CANCELADO
```

### Transiciones válidas

| Estado actual | Puede pasar a | Quién puede hacerlo |
|---------------|---------------|---------------------|
| Pendiente | Pagado, Cancelado | Sistema (pago) / Admin |
| Pagado | En preparación, Cancelado | Productor / Admin |
| En preparación | Enviado | Productor / Admin |
| Enviado | Entregado | Sistema / Admin |
| Entregado | — | Ninguno (estado final) |
| Cancelado | — | Ninguno (estado final) |

---

## 5. Procedimientos de gestión de stock

### PRO-STK-001 — Descuento automático de stock

```
INICIO
  │
  ├─► Se confirma un pedido (POST /api/orders)
  ├─► El backend itera sobre cada ítem del pedido
  ├─► Para cada ítem:
  │     ├─ Obtiene el producto desde Firestore
  │     ├─ Calcula nuevo stock: max(0, stock_actual - cantidad_pedida)
  │     └─ Actualiza campo stock en /products/{id}
  └─► El catálogo refleja el nuevo stock en tiempo real
FIN
```

### PRO-STK-002 — Producto sin stock

```
INICIO
  │
  ├─► El stock de un producto llega a 0
  ├─► En el catálogo: el producto muestra badge "Sin stock"
  ├─► En el detalle: el botón "Agregar al carrito" queda deshabilitado
  └─► El productor puede actualizar el stock editando el producto
FIN
```

---

## 6. Procedimientos de seguridad

### PRO-SEG-001 — Validación de token en cada request

```
INICIO
  │
  ├─► El frontend incluye el ID Token de Firebase en cada request:
  │     Authorization: Bearer <firebase_id_token>
  ├─► El middleware auth_middleware.py intercepta la request
  ├─► Verifica el token con Firebase Admin SDK
  │     ├─ Token inválido o expirado → 401 Unauthorized
  │     └─ Token válido → Extrae uid y rol del token
  └─► La request continúa al controlador correspondiente
FIN
```

### PRO-SEG-002 — Rate limiting en autenticación

```
INICIO
  │
  ├─► El usuario intenta iniciar sesión
  ├─► El middleware rate_limit.py verifica intentos fallidos
  │     ├─ Menos de 5 intentos → Permite el intento
  │     └─ 5 o más intentos en los últimos 15 min → 429 Too Many Requests
  ├─► Si el intento falla:
  │     └─ Incrementa contador de intentos fallidos en memoria
  └─► Si el intento es exitoso:
        └─ Resetea el contador de intentos fallidos
FIN
```

### PRO-SEG-003 — Control de acceso por rol

| Endpoint | CONSUMER | PRODUCER | ADMIN |
|----------|----------|----------|-------|
| GET /api/products | ✅ | ✅ | ✅ |
| POST /api/products | ❌ | ✅ | ✅ |
| GET /api/cart | ✅ | ❌ | ✅ |
| POST /api/orders | ✅ | ❌ | ✅ |
| GET /api/orders | ✅ | ❌ | ✅ |
| PATCH /api/orders/{id}/status | ❌ | ✅ | ✅ |
| GET /api/sales | ❌ | ✅ | ✅ |
| GET /api/producers/{id} | ✅ | ✅ | ✅ |

---

## 7. Procedimientos de administración del sistema

### PRO-ADM-001 — Reiniciar el backend

```bash
# 1. Conectarse al servidor
ssh usuario@187.77.22.186

# 2. Detener el proceso actual
pkill -f uvicorn

# 3. Activar entorno virtual
cd /ruta/al/backend
source .venv/bin/activate

# 4. Iniciar el servidor
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > backend.log 2>&1 &

# 5. Verificar que está corriendo
curl http://localhost:8000/health
```

### PRO-ADM-002 — Compilar y distribuir el frontend

```bash
# 1. Navegar al frontend
cd OrigenX/FronEnd

# 2. Compilar para producción
npm run build

# 3. Los archivos quedan en dist/ listos para servir
#    desde cualquier servidor web (Nginx, Apache, etc.)

# 4. Para preview local del build
npm run preview
```

### PRO-ADM-003 — Monitorear logs del backend

```bash
# Ver logs en tiempo real
tail -f backend.log

# Ver últimas 100 líneas
tail -n 100 backend.log

# Buscar errores
grep "ERROR" backend.log
```

---

## 8. Manejo de errores y excepciones

### Formato estándar de errores (RNF-009.3)

Todos los errores del backend siguen el formato:

```json
{
  "error": {
    "code": "CODIGO_ERROR",
    "message": "Descripción legible del error",
    "fields": ["campo1", "campo2"]  // Solo en errores de validación
  }
}
```

### Códigos de error comunes

| Código HTTP | Código de error | Descripción |
|-------------|----------------|-------------|
| 400 | `VALIDATION_ERROR` | Campos inválidos o faltantes |
| 401 | `UNAUTHORIZED` | Token inválido o expirado |
| 403 | `FORBIDDEN` | Sin permisos para la operación |
| 404 | `NOT_FOUND` | Recurso no encontrado |
| 409 | `CONFLICT` | Conflicto (ej: email ya registrado) |
| 422 | `CART_EMPTY` | Carrito vacío al intentar crear pedido |
| 422 | `INSUFFICIENT_STOCK` | Stock insuficiente |
| 429 | `RATE_LIMIT_EXCEEDED` | Demasiados intentos de login |
| 500 | `INTERNAL_ERROR` | Error interno del servidor |

### Manejo en el frontend

```
Request falla
    │
    ├─► 401 → Redirige a /login (token expirado)
    ├─► 403 → Muestra mensaje "Sin permisos"
    ├─► 404 → Muestra página de error con botón "Volver"
    ├─► 422 → Muestra mensaje específico del error de negocio
    ├─► 429 → Muestra tiempo de espera restante
    └─► 500 → Muestra "Error interno, intenta nuevamente"
```

