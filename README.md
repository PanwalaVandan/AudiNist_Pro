# 🔐 AuditNIST Pro

Lightweight **Cybersecurity Audit Toolkit** designed to transform complex security frameworks into practical audit workflows.

AuditNIST Pro converts cybersecurity frameworks such as **NIST CSF, ISO 27001, CIS Controls, and COBIT** into structured audit checklists that security auditors can evaluate quickly and consistently.

The project follows a **local-first architecture**, allowing audits to run entirely in the browser without requiring a backend.

---

# 🌍 Language

English | [Español](README_ES.md)

---

# 🎯 Project Vision

Cybersecurity frameworks are powerful but often difficult to operationalize in real audits.

AuditNIST Pro aims to solve this by:

- transforming frameworks into structured machine-readable models
- converting controls into practical audit units
- allowing auditors to evaluate compliance and risk quickly
- generating structured audit summaries and reports

The long-term goal is to evolve toward a **modular GRC audit engine** capable of supporting multiple frameworks.

---

# ⚙️ Core Architecture

The project is structured into three layers.

## UI Layer

Responsible for the audit interface and reporting.


ui/auditnist-local.html


Features:

- audit checklist interface
- control evaluation
- report generation
- charts and summaries
- multilingual interface

Runs entirely in the browser.

---

## Audit Engine

Core logic responsible for framework management.


core/auditEngine.js


Responsibilities:

- manage selected framework
- load framework adapters
- maintain control structures
- coordinate evaluation logic

Uses a **framework adapter pattern**.

---

## Risk Engine


core/riskEngine.js


Responsible for calculating compliance and risk summaries.

Current scoring model:


compliant → low risk
partial → medium risk
non-compliant → high risk


Future versions will implement more advanced risk scoring.

---

# 🧩 Framework Adapters

Framework support is implemented using adapters.


frameworks/
├─ nist-csfAdapter.js
├─ iso27001Adapter.js
├─ cisAdapter.js
└─ cobitAdapter.js


Each adapter provides:


getKey()
getName()
getCategories()
getControlsByDomain()
getControlPlaceholder()
getAIContext()


This allows the engine to support multiple frameworks without modifying core logic.

---

# 📊 Supported Frameworks

| Framework | Status |
|--------|--------|
| NIST CSF 2.0 | Implemented |
| ISO 27001:2022 | Implemented |
| CIS Controls v8 | Implemented |
| COBIT 2019 | Implemented |

Backend multi-framework architecture is complete.  
Current work focuses on UI integration and reporting improvements.

---

# 🚀 Getting Started

Clone the repository:


git clone https://github.com/SUALBA/AudiNist_Pro


Open the application:


ui/auditnist-local.html


No backend required.

---

# 🛠 Development Focus

Current work focuses on improving the multi-framework user experience.

### High Priority

- dynamic category dropdown based on framework
- dynamic control ID placeholder
- framework persistence in saved audits
- improved reporting structure

### Medium Priority

- improved risk scoring model
- cross-framework mapping
- improved audit summaries

### Long Term

- multi-audit management
- collaboration features
- enterprise reporting

---

---

# 🧩 Contribution Opportunities

The project is actively evolving and contributions are welcome.

Below is a checklist of areas where help is currently needed.

### UI Integration

- [ ] Dynamic category dropdown based on selected framework
- [ ] Dynamic control ID placeholder (NIST → PR.AC-1, ISO → A.5.1, etc.)
- [ ] Update UI when framework changes
- [ ] Improve framework selector UX

---

### Reporting Improvements

- [ ] Add framework name in PDF reports
- [ ] Add framework name in TXT reports
- [ ] Framework-aware report filename (e.g. Audit_ISO27001_RPT001.pdf)
- [ ] Improve report layout and readability

---

### Persistence

- [ ] Save selected framework in localStorage
- [ ] Restore framework when application loads
- [ ] Store framework metadata when saving audit JSON

---

### Risk Engine Improvements

- [ ] Implement configurable risk scoring
- [ ] Support likelihood × impact scoring model
- [ ] Improve compliance summary calculations

---

### Developer Experience

- [ ] Add unit tests for AuditEngine
- [ ] Add unit tests for RiskEngine
- [ ] Improve project documentation
- [ ] Improve code comments in framework adapters

---

### Good First Issues (Recommended for new contributors)

- [ ] Improve UI layout for framework selector
- [ ] Improve documentation for framework adapters
- [ ] Add additional control descriptions
- [ ] Improve README diagrams

# 🤝 Contributing

Contributions are welcome.

Please read:


CONTRIBUTING.md


before opening a pull request.

---

# 🔐 Security Notice

AuditNIST Pro is an **audit assistance tool**.

It does **not replace professional cybersecurity audits or regulatory certifications**.

Audit results should always be reviewed by qualified security professionals.

---

# 📜 License

MIT License

---

# ⭐ Support the Project

If you find this project useful:

- give the repository a star
- open issues for improvements
- contribute new framework adapters