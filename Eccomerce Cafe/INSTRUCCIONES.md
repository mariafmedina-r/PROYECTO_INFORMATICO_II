# ☕ Coffee Commerce: Guía de Inicio Rápido

Bienvenido al proyecto **The Artisanal Connection**. Este documento detalla los pasos necesarios para desplegar tanto el backend como el frontend, además de la información sobre los usuarios de prueba.

---

## 🏗️ Requisitos Previos

Asegúrate de tener instalado:
- **Node.js 18+** y **npm**
- **Python 3.9+**

---

## 📂 Estructura del Proyecto

- `/backend`: API construida con FastAPI y SQLAlchemy (SQLite).
- `/frontend`: Aplicación SPA construida con React, Vite y Vanilla CSS Premium.

---

## 🚀 Despliegue del Backend (FastAPI)

El backend gestiona la lógica de negocio, el inventario y las órdenes.

1. **Navega al directorio del backend:**
   ```powershell
   cd backend
   ```

2. **Crea y activa un entorno virtual (Recomendado):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Inicia el servidor:**
   ```powershell
   uvicorn main:app --reload
   ```
   > El backend estará disponible en `http://127.0.0.1:8000`. La base de datos SQLite (`sql_app.db`) se creará y semillas de datos se insertarán automáticamente al iniciar por primera vez.

---

## 🎨 Despliegue del Frontend (React + Vite)

El frontend es una interfaz moderna y reactiva conectada al servidor.

1. **Navega al directorio del frontend:**
   ```powershell
   cd frontend
   ```

2. **Ejecución de Scripts (Solución de errores en Windows):**
   Si recibes un error de permisos al ejecutar `npm`, abre PowerShell como Administrador y corre:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Instala las dependencias:**
   ```powershell
   npm install
   ```

4. **Inicia el servidor de desarrollo:**
   ```powershell
   npm run dev
   ```
   > El frontend se abrirá usualmente en `http://localhost:5173/` (o el puerto siguiente si está ocupado).

---

## 👤 Usuarios y Datos de Prueba

El sistema viene pre-configurado con datos iniciales para facilitar el desarrollo:

### Usuario Administrador / Comprador
- **Email:** `test@example.com`
- **Contraseña:** `testpassword123`
- **Rol:** Admin / Customer

### Catálogo Semilla
Al iniciar el backend, se cargan automáticamente:
- **Variedades de Café:** Gesha, Caturra, Castillo.
- **Productores:** Mateo Rivera, Familia Ospina, Beatriz Mendez.
- **Variantes:** Diferentes moliendas y precios con IVA del 19% pre-calculado.

---

## 🛠️ Notas de Desarrollo

- **Manejo de Errores:** Tanto el frontend como el backend tienen sistemas de logs y notificaciones visuales (Toasts) para informar sobre fallos de conexión o falta de stock.
- **CORS:** El backend permite conexiones de cualquier origen para facilitar las pruebas locales.
