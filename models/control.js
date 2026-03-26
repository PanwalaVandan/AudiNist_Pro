/**
 * ---------------------------------------------------------
 * AuditNIST Pro — Control Model
 * ---------------------------------------------------------
 * Defines the structure of a control within an audit session.
 *
 * A control represents an individual requirement from
 * a cybersecurity framework such as:
 * - NIST CSF
 * - ISO 27001
 * - CIS Controls
 * - COBIT
 *
 * Expected structure:
 *
 * {
 *   id: string,
 *   frameworkCode: string,
 *   title: string,
 *   question: string,
 *   domain: string,
 *   category: string,
 *   vertical: string,
 *   evaluation: {},
 *   evidence: string,
 *   notes: string
 * }
 *
 * Placeholder for future modular architecture.
 * ---------------------------------------------------------
 */