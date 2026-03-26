/**
 * -------------------------------------------------------------
 * AuditNIST Pro — UI Controller
 * -------------------------------------------------------------
 * Future modular architecture layer
 *
 * This file will act as the bridge between UI and Audit Engine
 * when the project moves from standalone HTML to modular structure.
 *
 * Currently not used in standalone version.
 * Kept for future architecture evolution.
 * -------------------------------------------------------------
 */

import { AuditEngine } from "../core/auditEngine.js";

export const auditEngine = new AuditEngine();

export function getFrameworkCategories() {
  return auditEngine.getCategories();
}

export function getControls(domain) {
  return auditEngine.getControlsByDomain(domain);
}

export function setFramework(key) {
  auditEngine.setFramework(key);
}

export function getSummary() {
  return auditEngine.getSummary();
}