/**
 * AuditNIST Pro — Core Audit Engine
 *
 * Current status:
 * - partially aligned with standalone UI
 * - future modular architecture entry point
 */


import { RiskEngine } from "./riskEngine.js";

import { NistAdapter } from "../frameworks/nist-csfAdapter.js";
import { IsoAdapter } from "../frameworks/iso27001Adapter.js";
import { CisAdapter } from "../frameworks/cisAdapter.js";
import { CobitAdapter } from "../frameworks/cobitAdapter.js";

export class AuditEngine {

  constructor() {
    this.controls = [];

    this.adapters = {
      "nist-csf": new NistAdapter(),
      "iso27001": new IsoAdapter(),
      "cis": new CisAdapter(),
      "cobit": new CobitAdapter()
    };

    this.evaluations = {};
    this.frameworkKey = "nist-csf";
  }

  setFramework(key) {
    if (this.adapters[key]) {
      this.frameworkKey = key;
    }
  }

  getAdapter() {
    return this.adapters[this.frameworkKey];
  }

  loadControls(controlsArray = []) {
    this.controls = controlsArray;
  }

  getSummary() {
    return RiskEngine.calculateSummary(this.controls);
  }

  getCategories() {
    return this.getAdapter().getCategories();
  }

  saveEvaluation(controlCode, evidence, compliance, risk, notes) {
    this.evaluations[controlCode] = {
      evidence,
      compliance,
      risk,
      notes
    };
  }

  addControl(controlCode) {
    if (this.controls.find(c => c.code === controlCode)) {
      return null;
    }

    const adapter = this.getAdapter();
    const categories = adapter.getCategories();

    for (const cat of categories) {
      const controls = adapter.getControlsByDomain(cat);
      const found = controls.find(c => c.code === controlCode);

      if (found) {
        const controlObj = {
          code: found.code,
          name: found.name,
          compliance: "unknown",
          risk: "unknown",
          evidence: "",
          notes: ""
        };

        this.controls.push(controlObj);
        return controlObj;
      }
    }

    return null;
  }

  
  addControlFromSCF(scfControl) {

    const mappedIds = scfControl.mappings[this.frameworkKey] || [];

    const controlObj = {
      scfId: scfControl.id,
      code: mappedIds.join(", "),
      name: scfControl.name,
      question: scfControl.question,
      guidance: scfControl.guidance,
      compliance: "unknown",
      risk: "unknown",
      evidence: scfControl.question,
      notes: ""
    };

    this.controls.push(controlObj);

    return controlObj;
  }

  getControlsByDomain(domain) {
    return this.getAdapter().getControlsByDomain(domain);
  }

  reset() {
    this.controls = [];
  }
}