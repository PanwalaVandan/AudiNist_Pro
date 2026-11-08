# Auto Analysis — single-call MVP (implementation reference)

**Status:** Phase 1 + 2 implemented and verified (mocked model). Awaiting
Railway testing (Phase 3–4).
**Lives in:** `ui/auditnist-local.html` (fork `PanwalaVandan/AudiNist_Pro`,
branch `deploy/railway`).
**Tracking:** [SUALBA/AuditSym#49](https://github.com/SUALBA/AuditSym/issues/49)
· contract agreed on [AuditSym-Methodology PR #1](https://github.com/SUALBA/AuditSym-Methodology/pull/1) (merged).

This document is the durable reference for the Auto Analysis rebuild so future
sessions can pick up without re-deriving context.

---

## 1. Why this change

The old Auto Analyze sent a per-control prompt and **auto-filled
compliance/risk** from a `{compliance, risk, notes, evidence}` reply — the exact
"retrieved text → verdict" shortcut SUALBA's methodology was built to stop (it
produced both the false negative and false positive in her End-to-End
validation). The agreed MVP makes the AI **propose, never decide**: a
non-authoritative signal the auditor reviews, with strict code-side validation.

### Agreed contract (from the methodology review)
- **Single model call** for the MVP (the two-pass Pass A / Pass B split is
  deferred).
- **Code-side validation** of every response; a breach routes the control to
  "requires manual review", never a silent apply.
- **Auditor-reviewed proposals** — the AI never sets `.cumple`/`.riesgo`.
- **SCF `guidance`** as the provisional criterion source (verbatim framework
  text isn't captured yet).
- **Population/sample capture deferred.** Where a requirement is
  population-dependent and coverage is unknown → `INSUFFICIENT_EVIDENCE`, but
  still list the supported aspects.
- **Report-layer items tracked separately** (finding grouping, "Key Strength %",
  certification disclaimer — these are PDF/report concerns, not the prompt).

---

## 2. Phase 1 implementation plan (as executed)

Port the Sep-25 prototype's Auto-Analysis layer
(`AuditSym-Methodology/00_VANDAN_REVIEW/prototype/…html`) into our current app,
**folded from two model calls to one**, reusing its validators + review UI
verbatim (they're good) and rewiring context to data our app actually has.

1. **Engine functions** (new), near the existing Auto Analyze code:
   - `aaContext(ctrlEl)` — builds the control context from the DOM/engagement
     fields.
   - `aaParseJSON`, `aaPrepareChunks` (rank top-5 + deterministic truncation
     signal), `aaExactQuote` (citation-fidelity check).
   - `aaValidateQualification` — validates the `evidence[]` array (one item per
     excerpt, quote is an exact substring, enum/date checks).
   - `aaValidateProposal` — the invariant validator (field whitelist, enums,
     `authoritative===false`, forbidden-word check skipping quotes,
     `LIKELY_SUPPORTED` gating, `LIKELY_PARTIAL` needs a positive aspect,
     emits `reviewFlags`).
   - `aaBuildPrompt` — the **single merged prompt** (qualify evidence + assess
     in one answer).
   - `aaAssessControl` — one `callAI`, then `aaValidateQualification` +
     `aaValidateProposal` on the same response.
   - `aaInsufficientProposal` — the no-evidence result built without a model
     call.
   - `aaRenderProposal`, `aaCopyDraft`, `aaProposals` (Map) — review-card UI +
     "copy proposal to evidence draft".
2. **Context wiring** (what our app can feed today): `criterion_text` ← SCF
   `guidance`; `criterion_version` ← framework name; `evaluated_entity` ←
   `empresa_auditada`; `scope`/`exclusions`/`engagement_period` ← `eng_*`
   fields; `relevant_population`/`sample_examined` ← empty (`UNKNOWN`, surfaced
   as review flags).
3. **Rewire `runAutoAnalysis`**: per control → RAG query → no chunks ⇒
   `INSUFFICIENT_EVIDENCE` card (no model call) → else `aaAssessControl` →
   `aaRenderProposal`; validator throw ⇒ "requires manual review". **Remove the
   compliance/risk auto-fill.**
4. **UI**: add an `#aa-review-list` proposal container to the modal; clear it at
   run start.

---

## 3. Work done (this build)

**File:** `ui/auditnist-local.html` (+261 / −116 before cleanup; the engine is
one contiguous block above `runAutoAnalysis`).

- **Added** the engine: `aaProposals`, `aaContext`, `aaParseJSON`,
  `aaPrepareChunks`, `aaExactQuote`, `aaValidateQualification`,
  `aaDecisionFields`, `aaValidateProposal`, `aaInsufficientProposal`,
  `aaBuildPrompt`, `aaAssessControl`, `aaRenderProposal`, `aaCopyDraft`.
- **Single-call fold:** `aaAssessControl` makes one `callAI(aaBuildPrompt(...))`
  returning `{evidence:[…], …assessment…}`, then validates qualification and
  (destructuring `evidence` out) the proposal with the same two validators the
  prototype used for its two calls.
- **Behavior switch:** `runAutoAnalysis` no longer sets `.cumple`/`.riesgo`/
  `.notes`/`.evidencia`. It renders proposal cards; the done-state now reports
  `📋 proposals · ⚪ no evidence · ❌ manual review` and states "AI proposals do
  not change compliance or risk." Removed the "already evaluated" overwrite
  gate (proposals never overwrite).
- **UI:** added `#aa-review-list` to the Auto Analyze modal (`#aa-body`),
  cleared on each run.
- **Copy-to-draft:** `aaCopyDraft` writes the proposal into the control's
  evidence field as a draft using the existing `AI_DRAFT_MARKER`, re-checking
  the context hasn't changed; it never touches compliance/risk.
- **Dead code removed:** the old `buildControlAnalysisPrompt`, the
  `promptOverwrite` helper, and the `overwriteResolver` global.

### Validators / invariants enforced (code-side)
`authoritative===false` and `auditor_review_required===true`; all enums in
range; evidence quotes are exact substrings of the retrieved text; no
`Cumple/Parcial/No Cumple/Compliant/Non-Compliant` in any AI-authored field
(quotes/sources exempt); `LIKELY_SUPPORTED` requires criterion+entity+population
+ period `ALIGNED` + population coverage + an `OPERATING_EFFECTIVENESS` item;
`LIKELY_PARTIAL` requires a positive aspect; a directional signal requires ≥1
relevant evidence item; truncation risk must be consistent with the computed
signal. Any breach ⇒ control marked "requires manual review".

### Verification (mocked `callAI`, no RAG/Ollama needed)
- Page parses, no console errors, 17/17 lifecycle unit tests pass.
- Good response → validates into a proposal and renders a card + copy button.
- Forbidden-word breach (`"Compliant"` in `requirement`) → **rejected** →
  manual review.
- No-evidence control → `INSUFFICIENT_EVIDENCE`, **no model call**.

---

## 4. Deferred (agreed, not in MVP)
- True two-call Pass A / Pass B split (Appendix A of the contract).
- Capturing `relevant_population` / `sample_examined` in the data model, and
  gating `LIKELY_SUPPORTED` on real population coverage.
- Per-control criterion/population inputs in the UI.
- Verbatim framework criterion text (SCF `guidance` is the stand-in).
- Report-layer D/E/F (finding grouping, distribution-as-conclusion,
  certification disclaimer).

---

## 5. How to test / next steps
- **Phase 3 (real model):** run the local RAG server + Ollama (or a configured
  provider in AI Settings), upload a document, open **Auto Analyze**, Start.
  Expect: proposal cards (not auto-filled fields), no-evidence controls as
  `INSUFFICIENT_EVIDENCE`, malformed/invariant-violating responses as "requires
  manual review". Easiest done on Railway with a stronger model than the local
  `qwen2.5:3b`, which may struggle with the full JSON contract.
- **Phase 4 (deploy):** push `deploy/railway` → fork → Railway redeploys for
  Susana to test. Kept on the fork (not upstreamed to her `main`) until
  validated.
- **Phase 5:** iterate on feedback (prompt tuning, validator thresholds, UI).

### Where things are (for a future session)
- Engine + run loop + modal: `ui/auditnist-local.html`, search `aaAssessControl`
  / `runAutoAnalysis` / `aa-review-list`.
- Contract + prototype: `SUALBA/AuditSym-Methodology/00_VANDAN_REVIEW/`.
- Methodology reasoning: that repo's List 3 + the End-to-End validation.
