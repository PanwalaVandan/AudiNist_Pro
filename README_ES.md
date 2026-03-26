# 🔐 AuditNIST Pro

> **Espacio de trabajo de auditoría de ciberseguridad multi-framework y local-first**
> Diseñado para ayudar a auditores, equipos de seguridad y profesionales de cumplimiento a realizar evaluaciones estructuradas con claridad, velocidad y una visión visual.

AuditNIST Pro es un espacio de trabajo de auditoría de ciberseguridad en evolución que reúne la **evaluación de controles, la visibilidad de riesgos, el seguimiento de evidencias, plantillas reutilizables y la generación de informes** en una única interfaz.

Actualmente soporta:

- **NIST CSF 2.0**
- **ISO 27001**
- **CIS Controls v8**
- **COBIT 2019**

---
## 🤝 Colaboración

AuditNIST Pro se desarrolla activamente con contribuciones de:

- **Susana Alba Santamaria** — Creadora del Proyecto
- **Vandan Panwala** — Colaborador Principal y Contribuyente de Arquitectura

GitHub: https://github.com/PanwalaVandan

## Por qué este proyecto destaca

Los marcos de ciberseguridad son potentes, pero en la práctica a menudo son:

- difíciles de operacionalizar
- fragmentados en diferentes documentos
- repetitivos de evaluar
- difíciles de visualizar en un flujo de trabajo limpio

**AuditNIST Pro** tiene como objetivo transformar esa complejidad en una experiencia más práctica:

- evaluar controles
- clasificar el cumplimiento
- puntuar el riesgo
- documentar evidencias
- reutilizar controles
- exportar resultados
- comparar el progreso del marco

Todo desde un **espacio de trabajo local-first**, sin necesidad de backend para el flujo de trabajo central.

---

## 📸 Vista Previa de la Interfaz

### Panel de Control Multi-Framework

![Panel de Control Multi-Framework](screenshots/dashboardRisk1.jpg)

Una visión general visual de la actividad de auditoría a través de los marcos, con métricas resumidas, visibilidad de cumplimiento y monitoreo orientado al riesgo.

---

### Flujo de Trabajo de Evidencia Asistido por IA

![Flujo de Trabajo de Evidencia Asistido por IA](screenshots/AI%20Evidence2.jpg)

Diseñado para soportar un proceso de auditoría más eficiente con manejo estructurado de evidencias y un flujo de documentación orientado al auditor.

---

### Controles Sugeridos por Dominio

![Controles Sugeridos](screenshots/Suggestcontrols3.jpg)

Las sugerencias de control conscientes del marco ayudan a acelerar la preparación de la auditoría y hacen que el flujo de trabajo sea más práctico.

---

### Selección de Dominio del Marco

![Selección de Dominio del Marco](screenshots/Suggestdomain6.jpg)

Los controles pueden explorarse desde una perspectiva de dominio, lo que facilita el uso de la herramienta para sesiones de auditoría reales.

---

### Seguimiento del Progreso del Marco

![Seguimiento del Progreso del Marco](screenshots/frameworkProgress4.jpg)

Las barras de progreso facilitan la visualización de la cobertura de evaluación en NIST, ISO, CIS y COBIT de un vistazo.

---

### Vista General de la Cuadrícula de Controles

![Vista General de la Cuadrícula de Controles](screenshots/gridControls5.jpg)

Un mapa de control más visual ayuda a identificar los elementos evaluados y mejora la legibilidad de la auditoría.

---

### Espacio de Trabajo de Controles del Marco

![Espacio de Trabajo de Controles del Marco](screenshots/Frameworkcontrols3.jpg)

El espacio de trabajo principal se basa en el manejo práctico de los controles: cumplimiento, riesgo, notas y evidencias.

---

### Vista de Informes

![Vista de Informes](screenshots/SCREENSHOT1.jpg)

AuditNIST Pro está diseñado para soportar la generación de informes estructurados y un flujo de trabajo de salida de auditoría más limpio.

---

## ✨ Características Actuales

### Soporte multi-framework

- NIST CSF 2.0
- ISO 27001
- CIS Controls v8
- COBIT 2019

### Espacio de trabajo de auditoría

- Evaluación de controles
- Clasificación de cumplimiento
- Calificación de riesgo
- Notas del auditor
- Seguimiento de evidencias
- Controles sugeridos
- Plantillas reutilizables

### Panel de control y análisis

- Resumen de cumplimiento
- Visualización de riesgos
- Progreso del marco
- Comparación multi-framework
- Métricas de auditoría

### Informes y portabilidad

- Exportación a PDF
- Exportación/importación JSON
- Historial de auditoría local
- Manejo estructurado de metadatos

### Diseño local-first

- No requiere backend
- Posibilidad de uso autónomo
- Persistencia en LocalStorage
- Modelo de despliegue ligero

---

## 🎯 Para quién es esto

### Auditores y profesionales de cumplimiento

- Auditores de ciberseguridad
- Equipos de auditoría interna
- Profesionales de GRC
- Especialistas en cumplimiento

### Equipos de seguridad

- Analistas SOC
- Ingenieros de seguridad
- Analistas de riesgos
- Consultores de seguridad

### Contribuyentes

- Desarrolladores frontend
- Constructores con mentalidad de seguridad
- Colaboradores de código abierto
- Personas interesadas en herramientas de auditoría, UX de cumplimiento e ideas de productos de seguridad

---

## 🧠 Visión del Proyecto

AuditNIST Pro está evolucionando hacia una plataforma de auditoría de ciberseguridad más estructurada y práctica, centrada en:

- evaluaciones multi-framework
- lógica de auditoría reutilizable
- pensamiento inter-framework
- mejor visualización del cumplimiento y el riesgo
- documentación de auditoría más eficiente
- futuros flujos de trabajo de auditoría asistidos por IA

Este **aún no es un producto terminado**, pero ya es más que una simple demostración o lista de verificación. Es un espacio de trabajo activo que avanza hacia una dirección de producto más clara.

---

## 🤝 Cómo Contribuir

AuditNIST Pro da la bienvenida a colaboradores en diferentes niveles.

Ya sea que desee mejorar la interfaz, refinar la lógica o ayudar a dar forma a la arquitectura, hay espacio para contribuir.

### 🟢 Nivel 1 — Contribuciones Rápidas

Buenas tareas para empezar:

- [ ] Mejorar el espaciado de la UI
- [ ] Mejorar el diseño de la tarjeta de control
- [ ] Mejorar el estilo del panel de control
- [ ] Mejorar la capacidad de respuesta
- [ ] Mejorar la legibilidad de los gráficos
- [ ] Mejorar la UI de la biblioteca de plantillas
- [ ] Mejorar la accesibilidad
- [ ] Mejorar la consistencia del modo oscuro

### 🔵 Nivel 2 — Mejoras Centrales

Contribuciones más técnicas:

- [ ] Refactorizar el Motor de Auditoría
- [ ] Mejorar el modelo de datos de control
- [ ] Mejorar la persistencia de la evaluación
- [ ] Mejorar los cálculos del panel de control
- [ ] Mejorar la lógica de importación/exportación
- [ ] Mejorar la gestión del estado
- [ ] Mejorar el rendimiento con auditorías grandes

### 🟣 Nivel 3 — Ideas Avanzadas

Contribuciones orientadas al futuro:

- [ ] Motor de mapeo inter-framework
- [ ] Modelo de puntuación de madurez
- [ ] Motor de puntuación de riesgos
- [ ] Normalización de controles
- [ ] Motor de recomendaciones de auditoría
- [ ] Asistente de auditoría con IA

---

## 🏗️ Dirección de la Arquitectura

AuditNIST Pro está evolucionando hacia una estructura construida alrededor de:

- Motor de Auditoría
- Adaptadores de Framework
- Registro de Evaluación
- Biblioteca de Plantillas
- Motor de Informes
- Capa de IA

Esta dirección facilita el crecimiento del proyecto y que los colaboradores trabajen de forma independiente.

---

## 🛣️ Hoja de Ruta

### Fase 1 — Fundación
- Soporte multi-framework
- Panel de control
- Controles de auditoría
- Informes
- Persistencia local

### Fase 2 — Estructura
- Arquitectura modular más limpia
- Mejor modelo de control
- Persistencia mejorada y flujo de auditoría
- Mejor experiencia para el contribuyente

### Fase 3 — Inteligencia
- Mapeo inter-framework
- Mejoras en la puntuación de riesgos
- Sugerencias más inteligentes
- Flujos de trabajo de auditoría asistidos por IA

---

## 🛠️ Pila Tecnológica

- HTML
- Tailwind CSS
- JavaScript
- Chart.js
- jsPDF
- FileSaver.js
- LocalStorage

---

## 🚀 Ejecutando el Proyecto

Abrir directamente:

```bash
open auditnist-local.html
```

O ejecutar un servidor local:

```bash
python -m http.server 8080
```

📌 Estado del Proyecto

Desarrollo activo — evolucionando hacia un espacio de trabajo estructurado de auditoría de ciberseguridad.

AuditNIST Pro se encuentra actualmente en una sólida fase pre-producto: utilizable, visible y en crecimiento.



# 👥 Contribuyentes Principales

### 👩‍💻 Autor
**Susana Alba Santamaria**
Constructora enfocada en Ciberseguridad y Auditoría
📧 sualba.dev@gmail.com

### 🤝 Colaborador Principal
**Vandan Panwala**
Contribuyente de Ciberseguridad e Ingeniería de Software
🔗 https://github.com/PanwalaVandan

Licencia

Licencia MIT

⭐ Apoya el Proyecto
Si encuentras este proyecto útil:

- dale una estrella al repositorio ⭐
- abre issues para mejoras
- contribuye con nuevos adaptadores de framework
