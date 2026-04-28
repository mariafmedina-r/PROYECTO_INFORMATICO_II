# 📚 Documentación – OrigenX / Conexión Cafetera

**MFRAL TECH Innovación y Soluciones Inteligentes**  
Universidad Autónoma de Occidente · Ingeniería Informática · 2026

---

## Índice de documentos

| Documento | Descripción |
|-----------|-------------|
| [manual-tecnico.md](./manual-tecnico.md) | Instalación, configuración y ejecución del sistema (Frontend + Backend) |
| [manual-usuario.md](./manual-usuario.md) | Guía de uso para consumidores y productores |
| [procedimientos.md](./procedimientos.md) | Procedimientos operativos y flujos del sistema |
| [arquitectura.md](./arquitectura.md) | Diagramas de arquitectura del aplicativo |

---

## Equipo

| Rol | Nombre |
|-----|--------|
| Developer | Edward Rubio Rodríguez |
| DevOps + Apoyo general |  Francisco Steven Tabares Ussa|
| Product Owner | Leonardo Martínez Franco |
| QA Engineer + Documentación | Maria Fernanda Medina Ramirez |

---

## Stack tecnológico

```
Frontend  →  React 18 + Vite 5 (servido localmente o servidor propio)
Backend   →  Python 3.12 + FastAPI + Uvicorn (expuesto vía ngrok HTTPS)
Base de datos  →  Firebase Firestore (NoSQL)
Autenticación  →  Firebase Authentication
Almacenamiento →  Firebase Storage
```

## URL de producción

- **Frontend:** Se sirve localmente o desde servidor propio
- **Backend API:** Local en `http://localhost:8000`
- **Documentación API:** `http://localhost:8000/docs`
