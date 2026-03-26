
/**
 * ---------------------------------------------------------
 * AuditNIST Pro — Ollama Provider
 * ---------------------------------------------------------
 * Current active AI provider for local-only generation.
 *
 * This provider supports AuditNIST Pro's local-first approach
 * and avoids dependency on external cloud APIs.
 *
 * Future architecture may add providers such as OpenAI,
 * while preserving the same provider interface.
 * ---------------------------------------------------------
 */

import { AIProvider } from "./aiProvider.js";

class OllamaProvider extends AIProvider {
  constructor(model = "qwen2.5:3b") {
    super();
    this.model = model;
  }

  async generateEvidence(prompt) {
    console.log("Ollama evidence generation (placeholder)");
    return "AI evidence placeholder";
  }

  async generateRecommendation(prompt) {
    console.log("Ollama recommendation (placeholder)");
    return "AI recommendation placeholder";
  }

  async generateGap(prompt) {
    console.log("Ollama gap generation (placeholder)");
    return "AI gap placeholder";
  }
}

export { OllamaProvider };



