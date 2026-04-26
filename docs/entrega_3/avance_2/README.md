# Entrega 3 - Avance 2

## Descripción

Este directorio contiene el segundo avance de la Entrega 3 del proyecto **Café Origen**, enfocado en la implementación técnica del MVP, ejecución de sprints y validación mediante pruebas funcionales.

## Contenido

- Documento del avance en formato PDF
- Archivo Excel con pruebas funcionales y no funcionales

## Objetivo del avance

Evidenciar el progreso técnico del sistema mediante:

- Implementación del MVP
- Ejecución de los sprints definidos
- Validación del sistema mediante pruebas
- Identificación de errores y oportunidades de mejora

A diferencia del avance anterior, este se enfoca en la ejecución real del sistema y su comportamiento en un entorno de desarrollo. :contentReference[oaicite:1]{index=1}

## Arquitectura del sistema

El sistema se desarrolla bajo una arquitectura cliente-servidor:

- Frontend: React + Vite
- Backend: FastAPI (Python)
- Base de datos: SQLite

El sistema permite la interacción entre usuario, productos y catálogo mediante consumo de API REST.

## Estado del MVP

Actualmente el sistema presenta:

- Registro y login: Implementado
- Gestión de productos: Implementado (con observaciones)
- Catálogo: Parcialmente implementado
- Carrito y pagos: En desarrollo

## Pruebas realizadas

Se ejecutaron pruebas funcionales y no funcionales para validar:

- Autenticación de usuarios
- Gestión de productos
- Visualización de catálogo
- Proceso de compra (parcial)

### Resultados

- Total de pruebas: 33
- Aprobadas: 20
- Fallidas: 13
- Pendientes: 12 

## Principales hallazgos

- Problemas en manejo de roles y sesiones
- Limitaciones en gestión de imágenes
- Fallos en filtros del catálogo
- Validaciones incompletas en formularios
- Flujo de compra aún no implementado completamente

## Tecnologías utilizadas

- React + Vite
- FastAPI
- SQLAlchemy
- SQLite
- GitHub
- Visual Studio Code

## Gestión del proyecto

El proyecto se gestiona mediante GitHub Projects, permitiendo:

- Seguimiento de tareas por sprint
- Visualización del estado del desarrollo
- Control del avance del equipo

## Limitaciones actuales

- Funcionalidades incompletas en catálogo y compra
- Falta de integración real de pagos
- Validaciones y experiencia de usuario en mejora

## Repositorio

https://github.com/mariafmedina-r/PROYECTO_INFORMATICO_II
