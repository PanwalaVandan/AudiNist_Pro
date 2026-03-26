/**
 * ---------------------------------------------------------
 * AuditNIST Pro — Evaluation Manager
 * ---------------------------------------------------------
 * Core module responsible for managing control evaluations.
 *
 * Intended responsibilities:
 * - store compliance evaluation
 * - store risk level
 * - store evidence and notes
 * - normalize evaluation structure
 * - support persistence and reporting integration
 *
 * This module will evolve as the audit engine becomes more
 * modular and structured.
 * ---------------------------------------------------------
 */

class EvaluationManager {
  constructor() {
    this.evaluations = {};
  }

  setEvaluation(controlId, compliance, risk, evidence = "", notes = "") {
    this.evaluations[controlId] = {
      compliance,
      risk,
      evidence,
      notes,
      updatedAt: new Date()
    };
  }

  getEvaluation(controlId) {
    return this.evaluations[controlId] || null;
  }

  getAll() {
    return this.evaluations;
  }

  reset() {
    this.evaluations = {};
  }
}

export { EvaluationManager };