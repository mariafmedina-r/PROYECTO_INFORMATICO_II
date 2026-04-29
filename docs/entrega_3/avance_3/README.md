#  Entrega 3 - Avance 3 (Versión 2 – OrigenX / Conexión Cafetera)

##  Descripción

Este directorio contiene el segundo avance de la Entrega 3 del proyecto **Café Origen**, correspondiente a la **versión evolucionada del sistema (OrigenX)**.

En esta versión se presenta la **reimplementación completa del MVP**, su validación mediante pruebas y la consolidación del flujo funcional del sistema.

A diferencia del avance anterior, esta entrega refleja un sistema **completamente funcional, estable y validado**, resultado de un proceso iterativo de desarrollo y mejora continua.

---

##  Contenido

- Documento del avance (Entrega III - Avance II - Versión Café OrigenX) en formato PDF  
- Archivo Excel con pruebas funcionales y no funcionales (Pruebas Versión Café OrigenX)
- Evidencias de gestión (GitHub Projects)  

---

##  Objetivo del avance

Evidenciar el estado actual del sistema mediante:

- Implementación completa del MVP  
- Ejecución y cierre de los sprints  
- Validación mediante pruebas funcionales y no funcionales  
- Corrección de hallazgos identificados  

---

##  Arquitectura del sistema

El sistema se desarrolla bajo una arquitectura cliente-servidor desacoplada:

- **Frontend:** React 18 + Vite  
- **Backend:** FastAPI (Python)  
- **Base de datos:** Firebase Firestore  
- **Autenticación:** Firebase Authentication  
- **Almacenamiento:** Firebase Storage  

La comunicación se realiza mediante API REST.

---

##  Estado del sistema (MVP)

El sistema se encuentra completamente implementado:

-  Registro e inicio de sesión  
-  Gestión de roles  
-  Gestión de productos  
-  Catálogo con filtros y búsqueda  
-  Carrito de compras  
-  Generación de pedidos  
-  Proceso de pago (simulado)  

---

##  Pruebas realizadas

Se ejecutaron pruebas funcionales y no funcionales para validar:

- Autenticación y control de acceso  
- Gestión de productos  
- Catálogo y filtros  
- Carrito y proceso de compra  
- Pedidos y pagos simulados  
- Usabilidad, rendimiento y compatibilidad  

---

##  Resultados

###  Pruebas funcionales

- Total: **32**  
- Aprobadas: **32**  
- Fallidas en ejecución inicial: **3**  
- Éxito final: **100%**

###  Pruebas no funcionales

- Total: **17**  
- Aprobadas: **17**  
- Éxito: **100%**

---

##  Principales hallazgos

Durante la ejecución inicial se identificaron:

-  Problemas en navegación entre roles  
-  Restricciones en selección de regiones  
-  Fallos en carga inicial de imágenes  

 Todos fueron corregidos y validados en reejecución.

---

##  Tecnologías utilizadas

- React + Vite  
- FastAPI  
- Firebase (Firestore, Auth, Storage)  
- GitHub  
- Visual Studio Code  

---

##  Gestión del proyecto

El proyecto se gestionó mediante **GitHub Projects**, permitiendo:

- Seguimiento de tareas por sprint  
- Control del avance  
- Trazabilidad de requerimientos  

---

##  Despliegue (entorno de prueba)

El sistema fue ejecutado en entorno local validando su funcionamiento completo.

###  Accesos

- Backend: http://127.0.0.1:8000  
- Docs API: http://127.0.0.1:8000/docs  
- Frontend: http://localhost:5173  

---

##  Repositorio

El código fuente está disponible en:

 https://github.com/mariafmedina-r/PROYECTO_INFORMATICO_II  

 ## Estructura del repositorio

Dentro del repositorio, el código fuente del sistema desarrollado (OrigenX) se encuentra organizado en la siguiente ruta:

- **OrigenX/** → Contiene el proyecto completo (frontend y backend)

Esta carpeta corresponde a la versión final del sistema implementado, incluyendo:

- Backend (FastAPI)
- Frontend (React + Vite)
- Integración con Firebase
- Lógica de negocio y estructura modular del sistema

Las demás carpetas del repositorio (docs, entregas, etc.) contienen la documentación y evidencias del proceso de desarrollo.

---

---
## Video del sistema

En el siguiente enlace se puede visualizar el video de presentación funcional del sistema, donde se evidencia el funcionamiento del MVP, los módulos implementados y el flujo completo de uso:

👉 [Enlace al video de la aplicación]  

---


---

##  Estado del proyecto

 Sistema completo, funcional y validado  
 Pruebas aprobadas al 100%  
 Flujo end-to-end implementado  

---
##  Equipo de trabajo

| Integrante | Rol | Responsabilidad |
|----------|------|---------------|
| **Edward Rubio Rodríguez** |  Developer / DevOps | Desarrollo completo del sistema, integración con Firebase y despliegue |
| **Francisco Stiven Tabares Ussa** |  Developer (fase inicial) | Participación en la implementación inicial |
| **Leonardo Martínez Franco** |  Product Owner | Gestión de requerimientos y validación funcional |
| **María Fernanda Medina Ramírez** |  QA Engineer / Documentación | Diseño y ejecución de pruebas, documentación del sistema |

---

 *El equipo demostró capacidad de adaptación ante cambios en el desarrollo, logrando la reimplementación y consolidación del sistema en su versión final funcional.*

