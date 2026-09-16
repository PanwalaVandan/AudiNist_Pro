"""
AuditSym — cloud RAG server (Railway).

Thin orchestrator. Does NO heavy ML itself: it calls Modal for PDF parsing
(DeepDoc) and for embedding, keeps the vectors in an in-memory FAISS index, and
answers per-control searches. Also serves the app's static files, so the UI and
the RAG API share one origin (no CORS, relative URLs).

Everything except /health sits behind HTTP Basic Auth so the deployment is not
openly accessible. The Modal endpoints it calls are separately bearer-token
gated. Secrets come only from env vars — nothing is hard-coded.

Env vars (set in Railway):
    PARSER_SERVICE_URL      DeepDoc parser base URL
    PARSER_SERVICE_SECRET   DeepDoc bearer token
    EMBED_SERVICE_URL       Embedding service base URL
    EMBED_SERVICE_SECRET    Embedding bearer token
    BASIC_AUTH_USER         username for the whole site
    BASIC_AUTH_PASS         password for the whole site
    PORT                    provided by Railway
"""

import os
import base64
import hmac
import threading
import secrets as _secrets

import numpy as np
import faiss
import httpx
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

EMBED_DIM = 384
PARSER_URL    = os.environ.get("PARSER_SERVICE_URL", "").rstrip("/")
PARSER_SECRET = os.environ.get("PARSER_SERVICE_SECRET", "")
EMBED_URL     = os.environ.get("EMBED_SERVICE_URL", "").rstrip("/")
EMBED_SECRET  = os.environ.get("EMBED_SERVICE_SECRET", "")
BASIC_USER    = os.environ.get("BASIC_AUTH_USER", "")
BASIC_PASS    = os.environ.get("BASIC_AUTH_PASS", "")

app = FastAPI(title="auditsym-cloud-rag")


# ── HTTP Basic Auth on everything except /health ───────────────────────────────
@app.middleware("http")
async def basic_auth(request: Request, call_next):
    if request.url.path == "/health" or not (BASIC_USER or BASIC_PASS):
        return await call_next(request)
    hdr = request.headers.get("authorization", "")
    ok = False
    if hdr.startswith("Basic "):
        try:
            user, _, pw = base64.b64decode(hdr[6:]).decode().partition(":")
            ok = hmac.compare_digest(user, BASIC_USER) and hmac.compare_digest(pw, BASIC_PASS)
        except Exception:
            ok = False
    if not ok:
        return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="AuditSym"'})
    return await call_next(request)


# ── In-memory per-session FAISS store (embeddings are already normalised, so
#    inner product == cosine similarity) ────────────────────────────────────────
_stores: dict[str, tuple] = {}  # session_id -> (index, chunks[])


def _store(session_id):
    if session_id not in _stores:
        _stores[session_id] = (faiss.IndexFlatIP(EMBED_DIM), [])
    return _stores[session_id]


# ── Modal calls ────────────────────────────────────────────────────────────────
def _infer_doc_type(name: str) -> str:
    n = name.lower()
    for key, val in (("soc2", "soc2"), ("soc_2", "soc2"), ("iso27001", "iso27001"),
                     ("iso_27001", "iso27001"), ("sig_lite", "sig_lite"),
                     ("sig_core", "sig_core"), ("hecvat", "hecvat"), ("caiq", "caiq"),
                     ("pentest", "pentest"), ("penetration", "pentest")):
        if key in n:
            return val
    return "other"


def _parse_pdf(pdf_bytes: bytes, filename: str) -> list[dict]:
    """DeepDoc parse -> our chunk shape {text, source, page, section_header}."""
    payload = {
        "pdf_b64": base64.b64encode(pdf_bytes).decode(),
        "filename": filename,
        "document_type": _infer_doc_type(filename),
    }
    with httpx.Client(timeout=620.0, follow_redirects=True) as c:
        r = c.post(f"{PARSER_URL}/parse", json=payload,
                   headers={"Authorization": f"Bearer {PARSER_SECRET}"})
        r.raise_for_status()
        data = r.json()
    return [
        {"text": ch["content"], "source": filename,
         "page": ch.get("page"), "section_header": ch.get("section_header")}
        for ch in data.get("chunks", []) if ch.get("content")
    ]


EMBED_BATCH = 512  # keep each embed request well under the service's caps

def _embed(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, EMBED_DIM), dtype=np.float32)
    # A real compliance PDF yields thousands of chunks — batch so no single
    # request exceeds the embed service's per-call limits.
    out = []
    with httpx.Client(timeout=620.0, follow_redirects=True) as c:
        for i in range(0, len(texts), EMBED_BATCH):
            r = c.post(f"{EMBED_URL}/embed", json={"texts": texts[i:i + EMBED_BATCH]},
                       headers={"Authorization": f"Bearer {EMBED_SECRET}"})
            r.raise_for_status()
            out.extend(r.json()["vectors"])
    return np.asarray(out, dtype=np.float32)


# DeepDoc parsing takes ~1s/page of GPU time, so a real compliance PDF holds a
# single HTTP request open for minutes — long enough for Railway's edge to drop
# it ("upstream error"). So /upload only kicks off the work and returns at once;
# the browser polls /status until it's ready. Parse+embed run in a background
# thread (sync httpx, so a thread rather than the event loop).
_status: dict[str, dict] = {}  # session_id -> {state, doc_count, chunk_count, error}


def _process_job(session_id: str, payloads: list[tuple[bytes, str]]):
    index, chunks = _store(session_id)
    try:
        doc_count = 0
        for raw, fname in payloads:
            parsed = _parse_pdf(raw, fname)
            if not parsed:
                continue
            vecs = _embed([c["text"] for c in parsed])
            index.add(vecs)
            chunks.extend(parsed)
            doc_count += 1
            _status[session_id].update(doc_count=doc_count, chunk_count=index.ntotal)
        _status[session_id]["state"] = "ready"
    except Exception as exc:
        _status[session_id].update(state="error", error=str(exc))


# ── API (contracts match the local rag/server.py so the UI is unchanged) ───────
class QueryRequest(BaseModel):
    session_id: str
    control_name: str = ""
    question: str = ""
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok", "service": "auditsym-cloud-rag"}


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...), session_id: str = Form(default="")):
    if not session_id:
        session_id = _secrets.token_urlsafe(12)
    # Read the uploaded bytes now (the file streams close once this returns),
    # then hand them to the background thread.
    payloads = [(await f.read(), f.filename) for f in files if f.filename]
    _store(session_id)
    _status[session_id] = {"state": "processing", "doc_count": 0, "chunk_count": 0, "error": None}
    threading.Thread(target=_process_job, args=(session_id, payloads), daemon=True).start()
    return {"session_id": session_id, "state": "processing"}


@app.get("/status/{session_id}")
def status(session_id: str):
    return _status.get(session_id, {"state": "unknown"})


@app.post("/query")
def query(req: QueryRequest):
    index, chunks = _store(req.session_id)
    q = f"{req.control_name} {req.question}".strip()
    if index.ntotal == 0 or not q:
        return {"chunks": []}
    vec = _embed([q])
    k = min(req.top_k, index.ntotal)
    scores, idx = index.search(vec, k)
    out = []
    for score, i in zip(scores[0], idx[0]):
        if i < 0:
            continue
        c = dict(chunks[i])
        c["score"] = float(score)
        out.append(c)
    return {"chunks": out}


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    _stores.pop(session_id, None)
    _status.pop(session_id, None)
    return {"deleted": session_id}


# ── Static: serve the app from the same origin (declared LAST so API wins) ──────
app.mount("/", StaticFiles(directory=".", html=True), name="static")
