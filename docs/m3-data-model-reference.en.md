# M3 — `remediationPlan` Data Model
### Quick Technical Reference · Remediation Hub

> This document is a reference map for whoever picks up the code, not end-user documentation. It describes the exact shape of the data, the state machine, and where each piece of logic lives in `remediation-hub.html`. Everything described here is verified by `regression_suite_hub.mjs` (sections 11–22).

---

## 1. Where things live (quick map)

| Concept | Function / constant | Approximate location |
|---|---|---|
| Empty plan schema | `createEmptyRemediationPlan(finding)` | ~L5171 |
| Legacy migration → plan | `ensureRemediationPlan(f)` + `migrateLegacyFieldsIntoPlan(f, plan)` | near `normalizeFinding()` |
| Backfilling new fields onto existing plans | `backfillRemediationPlanShape(plan)` | next to migration |
| State machine (allowed transitions) | `PLAN_ALLOWED_TRANSITIONS` | ~L3527 |
| Actual transition functions | `transitionPlanTo*`, `submitPlanForVerification`, `withdrawPlanSubmission`, `supersedePlan`, `cancelPlan` | ~L3690–3920 |
| Action/milestone/dependency/blocker CRUD | `addActionItem`, `completeActionItem`, `addMilestone`, `addDependency`, `resolvePlanBlocker`, etc. | ~L3960–4260 |
| Change requests (date extension) | `requestPlanChangeRequest`, `decidePlanChangeRequest` | ~L4300–4360 |
| Formal revisions | `createPlanRevision`, `MATERIAL_PLAN_FIELDS` | ~L4262 |
| Implementation evidence | `addImplementationEvidence`, `withdrawImplementationEvidence` | ~L4400–4440 |
| Derived progress / overdue | `calculatePlanProgress`, `isPlanOverdue`, `isPlanDueSoon` | next to the state machine |
| ID counters (`ACT-####`, etc.) | `state.remediationRegister`, `next*Id()` | ~L5100–5170 |
| Role gating (data layer, not just UI) | `canEditRemediationPlan()` — called inside **every** mutation function | next to `isPlanEditable()` |
| UI panel | `renderRemediationPlanPanel(f)` + `on*` handlers | after `renderManagementResponsePanel` |
| PDF reflection | inside `drawFindingCard()` in `generateHubPDF()` | the `if (plan) {...}` block |

---

## 2. Full `finding.remediationPlan` schema

```js
{
  planId: 'RMP-<sanitized findingId>',   // STABLE, never changes even if the plan is replaced
  revision: 1,                            // incremental; NEVER resets after a supersession (see §4)
  status: 'draft',                        // see state machine §3

  treatment: 'mitigate' | 'avoid' | 'transfer' | null,  // mirrors managementResponse.treatment

  objective: '', approach: '', scope: '',
  owner: { name: '', role: '', department: '' },              // execution owner
  accountableOwner: { name: '', role: '' },                    // accountable owner
  accountableOwnerNotRequiredReason: '',                       // the OR half of the acceptance criterion

  plannedStartDate: '', targetDate: '',   // targetDate is NEVER directly editable — only via changeRequest (§6)
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

  progressPercent: null,   // null ≠ 0 — null means "no active actions to weigh"

  submittedForVerificationAt: null,
  submittedForVerificationBy: null,
  submittedForVerificationByRole: null,

  changeRequests: [ /* §6 */ ],
  revisions: [ /* §4 */ ],
  history: [],             // append-only: {ts, field, from, to, actorName, actorRole, note}

  createdAt, createdBy, updatedAt, updatedBy,

  migratedFromLegacy: false,  // true ONLY if this came from pre-M3 data
  legacyNotes: []             // markers like 'owner_migrated_from_legacy_field'
}
```

**Sibling field on the finding**: `finding.supersededRemediationPlans: []` — archive of replaced plans (see §4). It does **not** live inside `remediationPlan`.

---

## 3. State machine

```
                 ┌─────────┐
  (eligible) ──▶ │  draft  │──cancelled──▶ [cancelled] (terminal)
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
                        └──────▶ back to in_progress

  From ANY non-terminal state ──supersedePlan()──▶ [superseded] (terminal)
```

- **There is no M3 path to `closed`.** `ready_for_verification` projects onto `finding.status = 'pending_validation'`, never onto `closed`. Only M5 can close a finding.
- `superseded` and `cancelled` are terminal — there is no transition back out.
- `PLAN_EDITABLE_STATUSES = ['draft', 'planned', 'in_progress', 'blocked']` — outside these, no content-mutation function acts (`isPlanEditable()`).

### Eligibility for having a plan (`ensureRemediationPlan`)

| Finding condition | `remediationPlan` |
|---|---|
| `validationStatus !== 'confirmed'` or no `treatment` | `null` |
| `validationStatus === 'disputed'` / `'closed_disputed'` | `null` |
| `treatment === 'risk_accepted'` | `null` (uses the risk-acceptance record instead of a plan) |
| `treatment` is `mitigate` / `avoid` / `transfer` | created in `draft` |

---

## 4. Revisions and treatment supersession

- Changing `treatment` while an active (non-terminal) plan exists **never** deletes the plan: it's marked `superseded`, archived into `finding.supersededRemediationPlans`, and a **new** plan is created with the **same `planId`**.
- The new plan's `revision` **continues** from the highest already-archived revision — it never resets to 1. Centralized function: `createReplacementRemediationPlan(f, reason, actor)` (used by both `onTreatmentChange()` and `confirmRiskAcceptance()` — previously duplicated, now unified).
- **Material** fields (`MATERIAL_PLAN_FIELDS`): `treatment, objective, scope, accountableOwner, completionCriteria, verificationCriteria, expectedResidualRisk`. Editing them via `onUpdatePlanField()` prompts for a reason and creates an entry in `plan.revisions[]` with a frozen `{field, before, after}` snapshot. **`targetDate` is excluded** from this list — it's never edited through this path (see §6).
- Non-material fields (e.g. `approach`) change directly, with no revision created.

---

## 5. Action (`actionItems[]`)

```js
{
  id: 'ACT-0001',
  title, description, owner, targetDate,
  status: 'not_started' | 'in_progress' | 'completed' | 'cancelled' | 'waived',
  weight: 10,                    // positive number, used in progress calculation
  completionCriteria: '',
  completedAt: null, completedBy: null,
  waiver: null | { reason, approvedBy, waivedAt, waivedBy }   // only valid if approvedBy+reason present
}
```

**Progress** (`calculatePlanProgress`): excludes `cancelled` and validly-`waived` items from the weighting base. Normalizes active weights to 100. Contribution: `completed` = full weight, `in_progress` = half, `not_started` = zero (`ACTION_PROGRESS_CONTRIBUTION`). No active actions → `null`, never `0`.

---

## 6. Change requests — the only path to `targetDate`

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

- `requestPlanChangeRequest()` **never** touches `plan.targetDate` — it only creates the pending record.
- Proposed-date validation: strict ISO format, a real calendar date (rejects `2026-13-45`), not earlier than `plannedStartDate`, and strictly **later** than the current `targetDate` (otherwise rejected as `proposed_date_not_an_extension`).
- `decidePlanChangeRequest()` only updates `targetDate` when `decision === 'approved'`, and in that case automatically creates a formal revision (`createPlanRevision`).

---

## 7. Milestones, dependencies, blockers

```js
// milestone
{ id: 'MLS-0001', title, targetDate, status: 'planned' | 'achieved', achievedAt, achievedBy }

// dependency
{ id: 'DEP-0001', description, owner, targetDate, status: 'open' | 'resolved', blocking: true }

// blocker (id does NOT use the central counter, derives from array length)
{ id: 'BLK-1', description, owner, impact, recordedAt, recordedBy,
  status: 'active' | 'resolved', resolvedAt, resolvedBy, resolution }
```

`ready_for_verification` requires: no unresolved blocking dependencies, no active blockers, progress at 100%.

---

## 8. Evidence — two distinct registers, don't conflate them

| | `EVD-####` (issue #34) | `REM-EVD-####` (M3) |
|---|---|---|
| Lives in | `control.evidenceItems[]` from the audit engine | `plan.implementationEvidence[]` in the Hub |
| Supports | the **original finding** | that the **remediation action** was actually carried out |
| Mutability in the Hub | immutable (read-only, carried through) | the Hub does create/withdraw it |
| Withdrawal | tombstone (`status: 'withdrawn'`, never physically deleted) | same: tombstone |

`withdrawImplementationEvidence()` is blocked if `!isPlanEditable(plan)` — evidence can't be withdrawn while the plan is `ready_for_verification`.

---

## 9. Identifier counters (`state.remediationRegister`)

```js
{ nextActionSequence, nextMilestoneSequence, nextDependencySequence, nextEvidenceSequence, nextChangeRequestSequence }
```

- **One per audit**, loaded/saved alongside `findings`/`history` (`loadRemediationRegister`/`saveRemediationRegister`).
- Exported in `exportHubJSON()`. Defensive normalization (`normalizeRemediationRegisterCounters()`) re-derives the true maximum by scanning **every** id actually embedded — including inside `supersededRemediationPlans` — so it can never collide even if the stored counter is stale.

---

## 10. Role gating — data layer, not just UI

- `canEditRemediationPlan() { return state.role === 'client'; }`
- Checked **inside all 23 mutation functions** (not only at render time). A role-based rejection returns `{ ok: false, errors: ['not_management_role'] }`.
- **This is client-side workflow gating to keep an honest user on the right rails — it is not authentication or real authorization.** The app has no backend and no login; anyone with devtools access could change `state.role`. This is disclosed both in `canEditRemediationPlan()`'s own comment, visibly in the UI (`plan_client_side_gating_disclosure`), and in the header of section 22 of the regression suite. **Never describe this as security.**

---

## 11. Legacy migration (one-time, idempotent)

`migrateLegacyFieldsIntoPlan()`, triggered only the first time a plan is created:

| Legacy field | Migrates to | Note |
|---|---|---|
| `finding.owner` | `plan.owner.name` | role is **never** fabricated |
| `finding.remediationNotes` | `plan.approach` | |
| `finding.evidenceFile` | `plan.implementationEvidence[]` | `status: 'legacy_unverified'`, never `'submitted'` |
| `status: 'pending_validation'` | `plan.status = 'ready_for_verification'` | **only** if `finding.submittedBy` exists (a real submission happened) |

`plan.migratedFromLegacy` + `plan.legacyNotes[]` flag exactly what was inferred.

---

## 12. PDF

Block inside `drawFindingCard()`, visually distinct (indigo accent) from the M2 block. Includes status/progress/date/overdue, owners, objective/approach/scope/priority/effort/cost/resources, actions/milestones/dependencies/evidence (**capped at 8 items per list** with a "+N more" indicator — `PDF_PLAN_LIST_CAP`, a preventive robustness measure, not a fix for a confirmed bug but a narrow safety margin found empirically), completion/verification criteria, and **expected residual risk with the literal label "(Management's Estimate, Not Auditor-Verified)"**.

---

## 13. Gotchas for whoever picks this up

- `targetDate` must **never** get a direct editable `<input>` again — only the change-request flow.
- Any **new** mutation function must include `if (!canEditRemediationPlan()) return { ok: false, errors: ['not_management_role'] };` — the pattern already established across the 23 existing ones.
- On re-import (`commitImportedAudit`), **both** `remediationPlan` **and** `supersededRemediationPlans` must be explicitly preserved (`existing.X || newF.X`) — `newF` comes straight from the imported payload and never carries either field.
- The `blocker` id (`BLK-N`) is the one exception to the centralized counter — it derives from `array.length + 1`, not `remediationRegister`. This works because blockers are never physically deleted, but it's inconsistent with the rest of the model if it's ever revisited.
- Playwright tests open each page with `state.role` defaulted to `'client'` (see `newPage()` in the suite) — if testing auditor behavior, override it explicitly.
