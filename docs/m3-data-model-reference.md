# M3 — Modelo de datos de `remediationPlan`
### Referencia técnica rápida · Remediation Hub

> Este documento es un mapa de referencia para quien retome el código, no documentación de usuario. Describe la forma exacta de los datos, la máquina de estados, y dónde vive cada pieza de lógica en `remediation-hub.html`. Todo lo aquí descrito está verificado por `regression_suite_hub.mjs` (secciones 11–22).

---

## 1. Dónde vive cada cosa (mapa rápido)

| Concepto | Función / constante | Ubicación aproximada |
|---|---|---|
| Esquema del plan vacío | `createEmptyRemediationPlan(finding)` | ~L5171 |
| Migración legacy → plan | `ensureRemediationPlan(f)` + `migrateLegacyFieldsIntoPlan(f, plan)` | cerca de `normalizeFinding()` |
| Relleno de campos nuevos en planes existentes | `backfillRemediationPlanShape(plan)` | junto a la migración |
| Máquina de estados (transiciones permitidas) | `PLAN_ALLOWED_TRANSITIONS` | ~L3527 |
| Funciones de transición reales | `transitionPlanTo*`, `submitPlanForVerification`, `withdrawPlanSubmission`, `supersedePlan`, `cancelPlan` | ~L3690–3920 |
| CRUD de acciones/hitos/dependencias/bloqueadores | `addActionItem`, `completeActionItem`, `addMilestone`, `addDependency`, `resolvePlanBlocker`, etc. | ~L3960–4260 |
| Change requests (extensión de fecha) | `requestPlanChangeRequest`, `decidePlanChangeRequest` | ~L4300–4360 |
| Revisiones formales | `createPlanRevision`, `MATERIAL_PLAN_FIELDS` | ~L4262 |
| Evidencia de implementación | `addImplementationEvidence`, `withdrawImplementationEvidence` | ~L4400–4440 |
| Progreso / overdue derivados | `calculatePlanProgress`, `isPlanOverdue`, `isPlanDueSoon` | junto a la máquina de estados |
| Contadores de ID (`ACT-####`, etc.) | `state.remediationRegister`, `next*Id()` | ~L5100–5170 |
| Gating de rol (dato, no solo UI) | `canEditRemediationPlan()` — llamada dentro de **cada** función de mutación | junto a `isPlanEditable()` |
| Panel de UI | `renderRemediationPlanPanel(f)` + manejadores `on*` | tras `renderManagementResponsePanel` |
| Reflejo en el PDF | dentro de `drawFindingCard()` en `generateHubPDF()` | bloque `if (plan) {...}` |

---

## 2. Esquema completo de `finding.remediationPlan`

```js
{
  planId: 'RMP-<findingId sanitizado>',   // ESTABLE, nunca cambia aunque el plan sea reemplazado
  revision: 1,                            // incremental; NUNCA reinicia tras una supersesión (ver §4)
  status: 'draft',                        // ver máquina de estados §3

  treatment: 'mitigate' | 'avoid' | 'transfer' | null,  // espejo de managementResponse.treatment

  objective: '', approach: '', scope: '',
  owner: { name: '', role: '', department: '' },              // responsable de ejecución
  accountableOwner: { name: '', role: '' },                    // propietario final
  accountableOwnerNotRequiredReason: '',                       // OR del criterio de aceptación

  plannedStartDate: '', targetDate: '',   // targetDate NUNCA editable directo — solo vía changeRequest (§6)
  priority: '' | 'low' | 'medium' | 'high' | 'critical',
  priorityOverrideReason: '',
  estimatedEffort: '',
  estimatedCost: { amount: null, currency: 'EUR', band: '' },
  resources: '',

  dependencies: [ /* §7 */ ],
  blockers: [ /* §7 */ ],
  actionItems: [ /* §5 */ ],
  milestones: [ /* §7 */ ],
  implementationEvidence: [ /* §8 */ ],

  completionCriteria: '', verificationCriteria: '',
  expectedResidualRisk: { likelihood: '', impact: '', level: '', rationale: '' },

  progressPercent: null,   // null ≠ 0 — null significa "sin acciones activas que pesar"

  submittedForVerificationAt: null,
  submittedForVerificationBy: null,
  submittedForVerificationByRole: null,

  changeRequests: [ /* §6 */ ],
  revisions: [ /* §4 */ ],
  history: [],             // append-only: {ts, field, from, to, actorName, actorRole, note}

  createdAt, createdBy, updatedAt, updatedBy,

  migratedFromLegacy: false,  // true SOLO si vino de datos pre-M3
  legacyNotes: []             // marcadores tipo 'owner_migrated_from_legacy_field'
}
```

**Campo hermano en el finding**: `finding.supersededRemediationPlans: []` — archivo de planes reemplazados (ver §4). **No** vive dentro de `remediationPlan`.

---

## 3. Máquina de estados

```
                 ┌─────────┐
  (elegible) ──▶ │  draft  │──cancelled──▶ [cancelled] (terminal)
                 └────┬────┘
                      │ transitionPlanToPlanned()
                      ▼
                 ┌─────────┐
                 │ planned │
                 └────┬────┘
                      │ transitionPlanToInProgress()
                      ▼
                 ┌─────────────┐   transitionPlanToBlocked()   ┌─────────┐
                 │ in_progress │ ────────────────────────────▶ │ blocked │
                 └──────┬──────┘ ◀──────────────────────────── └─────────┘
                        │           transitionPlanToInProgress()
                        │ submitPlanForVerification()
                        ▼
              ┌───────────────────────┐
              │ ready_for_verification│
              └───────────────────────┘
                        │ withdrawPlanSubmission()
                        └──────▶ vuelve a in_progress

  Desde CUALQUIER estado no terminal ──supersedePlan()──▶ [superseded] (terminal)
```

- **No existe ningún camino de M3 a `closed`.** `ready_for_verification` se proyecta a `finding.status = 'pending_validation'`, nunca a `closed`. Solo M5 puede cerrar.
- `superseded` y `cancelled` son terminales — no hay transición de vuelta.
- `PLAN_EDITABLE_STATUSES = ['draft', 'planned', 'in_progress', 'blocked']` — fuera de estos, ninguna función de mutación de contenido actúa (`isPlanEditable()`).

### Elegibilidad para tener plan (`ensureRemediationPlan`)

| Condición del finding | `remediationPlan` |
|---|---|
| `validationStatus !== 'confirmed'` o sin `treatment` | `null` |
| `validationStatus === 'disputed'` / `'closed_disputed'` | `null` |
| `treatment === 'risk_accepted'` | `null` (usa el registro de aceptación de riesgo, no un plan) |
| `treatment` en `mitigate` / `avoid` / `transfer` | se crea en `draft` |

---

## 4. Revisiones y supersesión de tratamiento

- Cambiar `treatment` con un plan activo (no terminal) **nunca** borra el plan: lo marca `superseded`, lo archiva en `finding.supersededRemediationPlans`, y crea un plan **nuevo** con el **mismo `planId`**.
- La `revision` del plan nuevo **continúa** la secuencia más alta ya archivada — nunca reinicia a 1. Función centralizada: `createReplacementRemediationPlan(f, reason, actor)` (usada por `onTreatmentChange()` y `confirmRiskAcceptance()` — antes duplicada, ahora unificada).
- Campos **materiales** (`MATERIAL_PLAN_FIELDS`): `treatment, objective, scope, accountableOwner, completionCriteria, verificationCriteria, expectedResidualRisk`. Editarlos vía `onUpdatePlanField()` pide motivo y crea una entrada en `plan.revisions[]` con snapshot congelado `{field, before, after}`. **`targetDate` está excluido** de esta lista — nunca se edita por este camino (ver §6).
- Campos no materiales (p. ej. `approach`) cambian directo, sin crear revisión.

---

## 5. Acción (`actionItems[]`)

```js
{
  id: 'ACT-0001',
  title, description, owner, targetDate,
  status: 'not_started' | 'in_progress' | 'completed' | 'cancelled' | 'waived',
  weight: 10,                    // número positivo, usado en el cálculo de progreso
  completionCriteria: '',
  completedAt: null, completedBy: null,
  waiver: null | { reason, approvedBy, waivedAt, waivedBy }   // solo válido si approvedBy+reason presentes
}
```

**Progreso** (`calculatePlanProgress`): excluye `cancelled` y `waived`-válidas de la base de ponderación. Normaliza pesos de las activas a 100. Contribución: `completed` = peso completo, `in_progress` = mitad, `not_started` = cero (`ACTION_PROGRESS_CONTRIBUTION`). Sin acciones activas → `null`, nunca `0`.

---

## 6. Change requests — únicas rutas hacia `targetDate`

```js
{
  id: 'CRQ-0001',
  type: 'target_date_extension',
  currentValue, proposedValue,
  reason, requestedAt, requestedBy, requestedByRole,
  status: 'pending' | 'approved' | 'rejected',
  decidedAt, decidedBy, decidedByRole, decisionNotes
}
```

- `requestPlanChangeRequest()` **nunca** toca `plan.targetDate` — solo crea el registro pendiente.
- Validación de la fecha propuesta: formato ISO estricto, fecha calendárica real (rechaza `2026-13-45`), no anterior a `plannedStartDate`, y estrictamente **posterior** a `targetDate` actual (si no, se rechaza como `proposed_date_not_an_extension`).
- `decidePlanChangeRequest()` solo actualiza `targetDate` si `decision === 'approved'`, y en ese caso crea automáticamente una revisión formal (`createPlanRevision`).

---

## 7. Hitos, dependencias, bloqueadores

```js
// milestone
{ id: 'MLS-0001', title, targetDate, status: 'planned' | 'achieved', achievedAt, achievedBy }

// dependency
{ id: 'DEP-0001', description, owner, targetDate, status: 'open' | 'resolved', blocking: true }

// blocker (id NO usa el contador central, deriva de longitud del array)
{ id: 'BLK-1', description, owner, impact, recordedAt, recordedBy,
  status: 'active' | 'resolved', resolvedAt, resolvedBy, resolution }
```

`ready_for_verification` exige: sin dependencias bloqueantes sin resolver, sin bloqueadores activos, progreso al 100%.

---

## 8. Evidencia — dos registros distintos, no confundir

| | `EVD-####` (issue #34) | `REM-EVD-####` (M3) |
|---|---|---|
| Vive en | `control.evidenceItems[]` del motor de auditoría | `plan.implementationEvidence[]` del Hub |
| Sustenta | el **hallazgo original** | que la **acción de remediación** se ejecutó |
| Mutabilidad en el Hub | inmutable (solo lectura, transportado) | el Hub SÍ la crea/retira |
| Retirada | tumba (`status: 'withdrawn'`, nunca borrado físico) | igual: tumba |

`withdrawImplementationEvidence()` bloqueada si `!isPlanEditable(plan)` — no se puede retirar evidencia con el plan en `ready_for_verification`.

---

## 9. Contadores de identificador (`state.remediationRegister`)

```js
{ nextActionSequence, nextMilestoneSequence, nextDependencySequence, nextEvidenceSequence, nextChangeRequestSequence }
```

- **Uno por auditoría**, cargado/guardado junto con `findings`/`history` (`loadRemediationRegister`/`saveRemediationRegister`).
- Exportado en `exportHubJSON()`. Normalización defensiva (`normalizeRemediationRegisterCounters()`) re-deriva el máximo real escaneando **todos** los IDs embebidos — incluidos los de `supersededRemediationPlans` — así que nunca colisiona aunque el contador guardado esté desactualizado.

---

## 10. Gating de rol — dato, no solo UI

- `canEditRemediationPlan() { return state.role === 'client'; }`
- Se comprueba **dentro de las 23 funciones de mutación** (no solo en el renderizado). Un rechazo por rol devuelve `{ ok: false, errors: ['not_management_role'] }`.
- **Esto es gating del lado del cliente para guiar el flujo de trabajo, no autenticación ni autorización real** — la app no tiene backend ni login; cualquiera con la consola del navegador podría cambiar `state.role`. Esta aclaración está tanto en el comentario de `canEditRemediationPlan()` como visible en la UI (`plan_client_side_gating_disclosure`) y en el encabezado de la sección 22 de la suite de pruebas. **Nunca describir esto como seguridad.**

---

## 11. Migración legacy (una sola vez, idempotente)

`migrateLegacyFieldsIntoPlan()`, disparada solo la primera vez que se crea el plan:

| Campo legacy | Migra a | Nota |
|---|---|---|
| `finding.owner` | `plan.owner.name` | rol **nunca** se fabrica |
| `finding.remediationNotes` | `plan.approach` | |
| `finding.evidenceFile` | `plan.implementationEvidence[]` | `status: 'legacy_unverified'`, nunca `'submitted'` |
| `status: 'pending_validation'` | `plan.status = 'ready_for_verification'` | **solo** si `finding.submittedBy` existe (envío real) |

Marcador `plan.migratedFromLegacy` + `plan.legacyNotes[]` deja rastro de qué se infirió.

---

## 12. PDF

Bloque dentro de `drawFindingCard()`, visualmente distinto (acento índigo) del bloque M2. Incluye estado/progreso/fecha/vencido, propietarios, objetivo/enfoque/alcance/prioridad/esfuerzo/coste/recursos, acciones/hitos/dependencias/evidencia (**capadas a 8 elementos por lista** con indicador "+N más" — `PDF_PLAN_LIST_CAP`, medida preventiva de robustez, no arregla un bug confirmado sino un margen de seguridad estrecho detectado empíricamente), criterios, y **riesgo residual con la etiqueta literal "(Estimación de Gestión, No Verificada por el Auditor)"**.

---

## 13. Gotchas para quien retome esto

- `targetDate` **jamás** debe volver a tener un `<input>` editable directo — solo el flujo de change request.
- Cualquier función de mutación **nueva** que se añada debe incluir `if (!canEditRemediationPlan()) return { ok: false, errors: ['not_management_role'] };` — patrón ya establecido en las 23 existentes.
- Al reimportar (`commitImportedAudit`), **tanto** `remediationPlan` **como** `supersededRemediationPlans` deben preservarse explícitamente (`existing.X || newF.X`) — `newF` viene del payload importado y nunca trae estos campos.
- El ID de `blocker` (`BLK-N`) es la única excepción al contador centralizado — deriva de `array.length + 1`, no de `remediationRegister`. Funciona porque los bloqueadores nunca se eliminan físicamente, pero es inconsistente con el resto del modelo si alguna vez se revisa.
- Las pruebas de Playwright abren cada página con `state.role` por defecto `'client'` (ver `newPage()` en la suite) — si se prueba comportamiento de auditor, hay que sobrescribirlo explícitamente.
