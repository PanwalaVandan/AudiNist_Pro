# How AuditSym analyses a PDF (Auto Analyze pipeline)

Your browser sends the PDF to our Railway server, which farms the heavy AI work out to two Modal services, keeps the results, and then answers a smart search for every control on the page. Nothing heavy runs on your laptop.

> For **which service does each step and how often** (does it re-parse per query? is Modal called on a query? where does the search run?), see [`rag-cloud-architecture.md`](rag-cloud-architecture.md) and its diagram.

## Step by step

1. **Upload** — In the Audit Engine you drop a PDF. The browser sends it to our Railway server (behind the login).

2. **Parse (Modal · DeepDoc)** — Railway forwards the PDF to the DeepDoc service on Modal. It reads the document (layout + OCR + tables) and splits it into clean chunks, each tagged with its control ID (e.g. CC6.1, A.9.1.2) and page number.

3. **Embed (Modal · Embedding)** — Railway sends those chunks to the Embedding service on Modal, which turns each chunk into a vector (a numeric "meaning fingerprint"). Sent in batches so even a 1,500-chunk report goes through fine.

4. **Store** — Railway keeps those vectors in a fast in-memory search index (FAISS) for your session.

   *(Steps 2–4 are the slow part on the first run — the Modal services "cold start." After that it's quick.)*

5. **Per-control search + AI verdict** — Now, for each control on the page, the browser:
   - asks Railway to find the most relevant chunks for that control (semantic search over the index);
   - takes those few chunks and asks the AI model to judge the control against them;
   - the model returns a verdict → Compliance, Risk, Auditor Notes, and Evidence, which auto-fill that control.

6. **Review & issue** — You review/adjust the auto-filled answers, then Issue Final Report (locks the audit + snapshots the findings), and export the JSON.

7. **Remediation Hub** — Import that JSON into the Hub to manage the findings — priority matrix, owners, decisions, status, and management responses.

---

## Notes for later (not urgent)

A few things worth resolving before this pipeline ever touches a real client's confidential audit, not before then:

- **Data retention on Railway / Modal.** The PDF and its derived chunks/vectors travel to three external services. Worth confirming and documenting what retention policy each has, and whether the "session" FAISS index is genuinely destroyed afterward or persisted somewhere.
- **Classification vs. transmission.** AuditSym's own reports carry a Confidential / Internal Use / Public classification. Once real client audits go through this pipeline, it's worth confirming the classification is honored by the infrastructure handling it, not just by the generated document.
- **Login model.** Today's login is a shared password for internal testing. Before onboarding real clients, this needs a real multi-user model — at which point the Hub portfolio's isolation and M3's segregation of duties can move from client-side enforcement to genuinely backend-enforced.

None of these block continued internal testing — they matter once this moves toward client-facing use.
