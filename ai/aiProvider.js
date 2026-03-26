/**
 * ---------------------------------------------------------
 * AuditNIST Pro — AI Provider Interface
 * ---------------------------------------------------------
 * Base interface for AI providers.
 *
 * Future providers:
 * - Ollama (local)
 * - OpenAI
 * - Azure OpenAI
 * - Local LLM
 *
 * This file defines the common API for all AI providers.
 * ---------------------------------------------------------
 */

class AIProvider {
  async generateEvidence(prompt) {
    throw new Error("generateEvidence not implemented");
  }

  async generateRecommendation(prompt) {
    throw new Error("generateRecommendation not implemented");
  }

  async generateGap(prompt) {
    throw new Error("generateGap not implemented");
  }
}

export { AIProvider };