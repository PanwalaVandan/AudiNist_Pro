export class NistAdapter {
  getKey() { return "nist-csf"; }

  getName() { return "NIST CSF 2.0"; }

  getCategories() {
    return ["Identify", "Protect", "Detect", "Respond", "Recover"];
  }

  getControlPlaceholder() {
    return "PR.AC-1";
  }

  getAIContext() {
    return "NIST Cybersecurity Framework 2.0";
  }
}