##  Avance – Pruebas Funcionales y No Funcionales (Entrega II / III)

En esta fase del proyecto *Marketplace Cafetero*, se definió y ejecutó una estrategia de pruebas orientada a la validación de los requerimientos funcionales y no funcionales del sistema, con el objetivo de garantizar la calidad, confiabilidad y correcto comportamiento de la plataforma.

##  Pruebas Funcionales

Las pruebas funcionales se diseñaron con base en las historias de usuario (HU) y criterios de aceptación definidos previamente. Estas pruebas permiten validar que cada funcionalidad del sistema cumpla con el comportamiento esperado desde la perspectiva del usuario.

###  Alcance

- Gestión de productos (creación, edición, visualización)
- Carga y asociación de imágenes
- Visualización en catálogo
- Filtros por categoría de productos
- Flujo básico de interacción usuario-sistema

###  Metodología

Se implementaron casos de prueba estructurados con los siguientes elementos:
- ID de prueba (ej. PF-015, PF-025)
- Historia de usuario asociada
- Precondiciones
- Pasos de ejecución
- Resultado esperado vs resultado actual
- Evidencia de ejecución

###  Hallazgos relevantes

- **PF-015:** Inconsistencia en la visualización de imágenes al crear productos. La imagen no se muestra en el primer guardado, requiriendo una edición posterior para su correcta visualización.
- **PF-025:** No es posible validar el filtro por categoría en productos de café, debido a la ausencia de una categorización estructurada (clasificación basada únicamente en nombre).

Estos hallazgos evidencian problemas en la persistencia de datos y en el diseño del modelo de información del sistema.

---

##  Pruebas No Funcionales

Las pruebas no funcionales se orientaron a evaluar atributos de calidad del sistema, alineados con estándares de ingeniería de software.

###  Características evaluadas

- **Usabilidad:**  
  Se evaluó la facilidad de uso en la carga de productos e interacción con el catálogo, identificando mejoras en retroalimentación visual (ej. visualización de imágenes).

- **Consistencia de datos:**  
  Se validó el comportamiento del sistema en la persistencia de información, detectando fallos en la sincronización entre almacenamiento y visualización.

- **Mantenibilidad:**  
  Se identificaron dependencias en el flujo de guardado que pueden afectar la estabilidad del sistema.

- **Escalabilidad (evaluación teórica):**  
  Basada en la arquitectura híbrida propuesta, se determinó que el sistema puede escalar mediante servicios desacoplados y APIs.

---

##  Conclusiones de pruebas

El proceso de pruebas permitió identificar defectos funcionales críticos relacionados con:
- Persistencia de datos
- Integridad de la información
- Diseño de atributos (categorías)

Asimismo, se evidenció la necesidad de fortalecer:
- Validaciones en frontend y backend
- Modelo de datos (normalización de categorías)
- Manejo de eventos en el flujo de guardado

Estas pruebas constituyen un insumo clave para la mejora continua del sistema y la preparación para fases posteriores de desarrollo.

---

## Equipo
- Edward Rubio Rodríguez – Developer  
- Francisco Tabares – DevOps  
- Leonardo Martínez – Product Owner  
- María Fernanda Medina – QA  
