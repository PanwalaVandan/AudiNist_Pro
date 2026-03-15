# 🔐 AuditNIST Pro

Herramienta ligera de **auditoría de ciberseguridad** diseñada para convertir frameworks complejos en flujos de auditoría prácticos.

AuditNIST Pro transforma frameworks como:

- NIST CSF
- ISO 27001
- CIS Controls
- COBIT

en listas estructuradas que los auditores pueden evaluar rápidamente.

La aplicación sigue una arquitectura **local-first**, ejecutándose completamente en el navegador.

---

# 🎯 Visión del Proyecto

Los frameworks de ciberseguridad son potentes pero difíciles de aplicar en auditorías reales.

AuditNIST Pro busca:

- convertir frameworks en modelos estructurados
- transformar controles en unidades auditables
- facilitar evaluaciones rápidas
- generar resúmenes de auditoría

El objetivo a largo plazo es crear un **motor de auditoría GRC modular**.

---

# ⚙️ Arquitectura

El proyecto se divide en tres capas:

### UI

Interfaz de auditoría:


ui/auditnist-local.html


### Audit Engine

Motor de auditoría:


core/auditEngine.js


### Risk Engine

Motor de cálculo de riesgo:


core/riskEngine.js


---

# 🧩 Frameworks soportados

| Framework | Estado |
|--------|--------|
| NIST CSF | Implementado |
| ISO 27001 | Implementado |
| CIS Controls | Implementado |
| COBIT | Implementado |

---

# 🤝 Contribuciones

Las contribuciones son bienvenidas.

Consulta:


CONTRIBUTING.md


---

# 📜 Licencia

MIT License