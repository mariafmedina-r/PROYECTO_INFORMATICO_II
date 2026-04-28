# 👤 Manual de Usuario – Conexión Cafetera

**MFRAL TECH** · Universidad Autónoma de Occidente · 2026

---

## Tabla de contenido

1. [Introducción](#1-introducción)
2. [Acceso a la plataforma](#2-acceso-a-la-plataforma)
3. [Registro de cuenta](#3-registro-de-cuenta)
4. [Inicio de sesión](#4-inicio-de-sesión)
5. [Módulo Consumidor](#5-módulo-consumidor)
6. [Módulo Productor](#6-módulo-productor)
7. [Página Origen](#7-página-origen)
8. [Directorio de Productores](#8-directorio-de-productores)
9. [Seguridad y sesión](#9-seguridad-y-sesión)
10. [Preguntas frecuentes](#10-preguntas-frecuentes)

---

## 1. Introducción

**Conexión Cafetera** es una plataforma digital tipo marketplace que conecta a productores de café colombiano con consumidores finales. Permite:

- Explorar el catálogo de cafés especiales de diferentes regiones del país
- Conocer el origen y la historia de cada productor
- Realizar compras directamente al productor
- Gestionar productos y ventas (para productores)

**URL de acceso:** Proporcionada por el administrador del sistema

---

## 2. Acceso a la plataforma

Al ingresar a la plataforma, el usuario verá la página de inicio **Origen**, que presenta las regiones cafeteras de Colombia. Desde la barra de navegación superior se puede acceder a:

```
┌─────────────────────────────────────────────────────────┐
│  Conexión Cafetera   Origen  Productores  Catálogo   ≡  │
└─────────────────────────────────────────────────────────┘
```

- **Origen** — Historia y regiones cafeteras
- **Productores** — Directorio de productores registrados
- **Catálogo** — Todos los productos disponibles
- **≡** — Menú en dispositivos móviles

---

## 3. Registro de cuenta

### Paso a paso

1. Hacer clic en **"Registrarse"** en la barra de navegación
2. Seleccionar el tipo de cuenta:
   - **Consumidor** — Para comprar productos
   - **Productor** — Para vender productos
3. Completar el formulario:

| Campo | Descripción | Requisito |
|-------|-------------|-----------|
| Nombre completo | Nombre y apellido | Obligatorio |
| Correo electrónico | Email válido | Obligatorio |
| Contraseña | Mínimo 8 caracteres | Obligatorio |
| Confirmar contraseña | Debe coincidir | Obligatorio |

4. Hacer clic en **"Crear cuenta"**
5. El sistema inicia sesión automáticamente

> ℹ️ Una vez creada la cuenta, el rol (Consumidor o Productor) **no puede cambiarse**.

---

## 4. Inicio de sesión

1. Hacer clic en **"Iniciar sesión"**
2. Ingresar correo electrónico y contraseña
3. Hacer clic en **"Ingresar"**

### Recuperar contraseña

1. En la pantalla de login, hacer clic en **"¿Olvidaste tu contraseña?"**
2. Ingresar el correo electrónico registrado
3. Revisar la bandeja de entrada y seguir el enlace recibido

> ⚠️ Por seguridad, la sesión se cierra automáticamente después de **5 minutos de inactividad**.

---

## 5. Módulo Consumidor

### 5.1 Explorar el catálogo

1. Hacer clic en **"Catálogo"** en la navegación
2. Usar los filtros disponibles:
   - **Búsqueda por nombre** — Escribir el nombre del producto
   - **Precio mínimo / máximo** — Rango de precios
   - **Región** — Filtrar por departamento de origen
3. Los resultados se actualizan automáticamente
4. Hacer clic en una tarjeta de producto para ver el detalle

### 5.2 Detalle del producto

En la página de detalle se muestra:
- Galería de imágenes (hacer clic para ampliar)
- Nombre, precio y stock disponible
- Descripción completa del producto
- Información del productor con enlace a su perfil
- Selector de cantidad
- Botón **"Agregar al carrito"**

### 5.3 Carrito de compras

1. Hacer clic en el ícono 🛒 en la barra de navegación
2. En el carrito se puede:
   - Modificar la cantidad de cada producto
   - Eliminar productos
   - Ver el subtotal y costo de envío
3. Hacer clic en **"Proceder al pago"** para continuar

### 5.4 Proceso de compra (Checkout)

**Paso 1 — Dirección de envío**
- Seleccionar una dirección guardada, o
- Agregar una nueva dirección:
  - Calle / Carrera
  - Ciudad
  - Departamento
  - Código postal

**Paso 2 — Empresa de envío**
- Seleccionar entre las opciones disponibles
- Cada opción muestra el costo y tiempo estimado de entrega

**Paso 3 — Pago**
- Ingresar los datos de la tarjeta de crédito/débito
- Hacer clic en **"Confirmar pedido"**

**Paso 4 — Confirmación**
- El sistema muestra el número de pedido
- El carrito se vacía automáticamente
- Se envía notificación de confirmación

### 5.5 Historial de pedidos

1. Hacer clic en **"Mis pedidos"** en la navegación
2. Se muestra la lista de todos los pedidos realizados con:
   - Número de pedido
   - Fecha
   - Estado actual
   - Total pagado
3. Hacer clic en un pedido para ver el detalle completo

### Estados de un pedido

```
Pendiente → Pagado → En preparación → Enviado → Entregado
                ↘                                    
              Cancelado
```

| Estado | Descripción |
|--------|-------------|
| 🟡 Pendiente | Pedido creado, esperando confirmación de pago |
| 🔵 Pagado | Pago confirmado, el productor lo está procesando |
| 🟣 En preparación | El productor está preparando el pedido |
| 🟢 Enviado | El pedido está en camino |
| ✅ Entregado | Pedido recibido exitosamente |
| ❌ Cancelado | Pedido cancelado |

### 5.6 Notificaciones

- La campana 🔔 en la barra de navegación muestra notificaciones de cambios de estado
- El número en rojo indica notificaciones sin leer
- Hacer clic en una notificación lleva al detalle del pedido correspondiente

### 5.7 Mi perfil

1. Hacer clic en **"Mi perfil"** en la navegación
2. Desde aquí se puede:
   - Ver y editar información personal
   - Gestionar direcciones de envío guardadas

---

## 6. Módulo Productor

### 6.1 Panel del productor

Después de iniciar sesión como productor, hacer clic en **"Mi panel"** en la navegación. El panel tiene tres pestañas:

```
┌──────────────────────────────────────────────┐
│  Mi Perfil  │  Mis Productos  │  Mis Ventas  │
└──────────────────────────────────────────────┘
```

### 6.2 Mi Perfil (pestaña)

Completar la información pública del perfil que verán los consumidores:

| Campo | Descripción |
|-------|-------------|
| Nombre de la finca | Nombre comercial del productor |
| Región | Departamento de Colombia |
| Descripción | Historia y filosofía de la finca (editor de texto enriquecido) |
| Correo de contacto | Email visible al público (opcional) |
| Correo alternativo | Segundo email de contacto (opcional) |
| WhatsApp | Número para contacto directo |
| Imágenes de la finca | Galería fotográfica (máximo 5 imágenes) |

Hacer clic en **"Guardar perfil"** para aplicar los cambios.

### 6.3 Mis Productos (pestaña)

#### Crear un nuevo producto

1. Hacer clic en **"+ Nuevo Producto"**
2. Completar el formulario:

| Campo | Descripción | Requisito |
|-------|-------------|-----------|
| Nombre | Nombre del producto | Obligatorio |
| Descripción | Descripción detallada (editor enriquecido) | Obligatorio |
| Precio | Precio en pesos colombianos (COP) | Obligatorio |
| Stock | Cantidad disponible | Obligatorio |

3. Subir imágenes del producto (máximo 5, formatos JPG/PNG)
4. Hacer clic en **"Guardar"**

#### Editar un producto

1. En la tabla de productos, hacer clic en **"✏️ Editar"**
2. Modificar los campos deseados
3. Hacer clic en **"Guardar"**

#### Activar / Desactivar un producto

- **Desactivar:** El producto deja de aparecer en el catálogo público
- **Activar:** El producto vuelve a ser visible en el catálogo

> ℹ️ La tabla muestra: Nombre, Precio, **Stock actual**, Estado y Acciones.

### 6.4 Mis Ventas (pestaña)

Muestra todos los pedidos que contienen productos del productor.

#### Resumen mensual

```
┌─────────────────┐  ┌─────────────────┐
│   Mes actual    │  │  Mes anterior   │
│   $ 520.000     │  │   $ 380.000     │
└─────────────────┘  └─────────────────┘
```

#### Filtrar por fecha

1. Ingresar fecha de inicio en **"Desde"**
2. Ingresar fecha de fin en **"Hasta"**
3. Hacer clic en **"Filtrar"**
4. Para quitar el filtro, hacer clic en **"Limpiar"**

#### Información de cada venta

Cada registro muestra:
- **Pedido** — Identificador único (últimos 8 caracteres)
- **Fecha** — Fecha de creación del pedido
- **Cliente** — Nombre, email y dirección de envío del comprador
- **Productos** — Lista de productos vendidos con cantidad y subtotal
- **Total** — Valor total del pedido
- **Estado** — Estado actual del pedido

#### Actualizar estado de un pedido

El productor puede avanzar el estado del pedido según el flujo:

```
Pagado → En preparación → Enviado
```

> ℹ️ Solo el productor cuyos productos están en el pedido puede cambiar su estado.

---

## 7. Página Origen

La página **Origen** presenta las regiones cafeteras de Colombia:

- **Antioquia** — Cafés de altura con notas frutales
- **Huila** — Reconocido por su acidez brillante
- **Nariño** — Altitudes extremas y perfiles únicos

Hacer clic en una región lleva al catálogo filtrado por esa región.

---

## 8. Directorio de Productores

1. Hacer clic en **"Productores"** en la navegación
2. Se muestra la lista de todos los productores registrados
3. Hacer clic en un productor para ver su perfil completo

### Perfil público del productor

El perfil muestra:
- Foto de portada y avatar
- Nombre de la finca y región
- Historia y descripción
- Galería de imágenes de la finca
- Productos disponibles
- Información de contacto (email y WhatsApp)

> 📱 En dispositivos móviles, los botones de contacto aparecen fijos en la esquina inferior derecha de la pantalla.

---

## 9. Seguridad y sesión

### Cierre automático de sesión

La sesión se cierra automáticamente después de **5 minutos sin actividad** para proteger la cuenta del usuario. Esto aplica tanto para consumidores como para productores.

### Bloqueo por intentos fallidos

Después de **5 intentos fallidos** de inicio de sesión, la cuenta queda bloqueada temporalmente por **15 minutos**.

### Recomendaciones de seguridad

- No compartir las credenciales de acceso
- Cerrar sesión manualmente al usar dispositivos compartidos
- Usar una contraseña segura (mínimo 8 caracteres, combinando letras y números)

---

## 10. Preguntas frecuentes

**¿Puedo cambiar mi rol de Consumidor a Productor?**
No. El rol se asigna al momento del registro y no puede modificarse.

**¿Cómo sé si mi pedido fue recibido?**
Recibirás una notificación en la campana 🔔 cuando el estado del pedido cambie. También puedes consultar el historial en "Mis pedidos".

**¿Puedo cancelar un pedido?**
Solo es posible cancelar un pedido cuando está en estado "Pendiente" o "Pagado". Una vez en preparación, no es posible cancelarlo.

**¿Qué pasa si un producto se agota?**
El stock se descuenta automáticamente con cada compra. Si el stock llega a 0, el producto muestra "Sin stock" y no puede agregarse al carrito.

**¿Cómo contacto a un productor?**
Desde el perfil público del productor encontrarás botones de contacto por email y WhatsApp.

**¿Mis datos de pago están seguros?**
Los pagos son procesados por una pasarela de pagos externa. La plataforma no almacena datos de tarjetas de crédito.

