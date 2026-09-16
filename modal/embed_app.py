"""
AuditSym — Modal embedding service.

Turns text chunks into 384-dim vectors using the same model the local RAG uses
(sentence-transformers/all-MiniLM-L6-v2), so nothing downstream (FAISS dim,
query flow) has to change.

Runs on CPU (this model doesn't need a GPU) and scales to zero between uses, so
it barely touches your Modal credit. The model weights are baked into the image
at build time, so cold starts don't re-download ~90 MB.

Security: /embed requires  Authorization: Bearer <AUDITSYM_EMBED_SECRET>.
Without the token it returns 401. The token lives in a Modal secret, never in
code. /health is open (liveness only, returns nothing sensitive).

Deploy:
    pip install modal                      # once
    modal token new                        # once, authenticates this machine
    # generate a strong token:
    python -c "import secrets; print(secrets.token_urlsafe(32))"
    modal secret create auditsym-embed-secret AUDITSYM_EMBED_SECRET=<that-token>
    modal deploy modal/embed_app.py
    # -> copy the printed https://...modal.run URL; keep the token for Railway
"""

import modal

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM  = 384

# Abuse guards for a public, internet-facing endpoint.
MAX_TEXTS       = 2000        # chunks per request
MAX_TOTAL_CHARS = 2_000_000   # ~500k tokens; a very large PDF still fits


def _bake_model():
    # Runs at image-build time so the weights live inside the image layer.
    from sentence_transformers import SentenceTransformer
    SentenceTransformer(MODEL_NAME)


image = (
    modal.Image.debian_slim()
    # CPU-only torch first — this service runs on CPU, so pulling the default
    # CUDA build (~2 GB of nvidia-* wheels) is pure waste and bloats the image.
    .pip_install("torch", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install("sentence-transformers==3.*", "fastapi[standard]", "numpy")
    .run_function(_bake_model)
)

app = modal.App("auditsym-embed")


@app.cls(
    image=image,
    secrets=[modal.Secret.from_name("auditsym-embed-secret")],
    cpu=2,
    scaledown_window=120,   # stay warm 2 min after last call to smooth batches
)
class Embedder:
    @modal.enter()
    def load(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(MODEL_NAME)

    @modal.asgi_app()
    def web(self):
        import os
        import hmac
        from fastapi import FastAPI, Header, HTTPException
        from pydantic import BaseModel

        secret = os.environ["AUDITSYM_EMBED_SECRET"]
        api = FastAPI(title="auditsym-embed")

        def check_auth(authorization: str | None):
            # Constant-time compare; reject anything that isn't the exact token.
            expected = f"Bearer {secret}"
            if not authorization or not hmac.compare_digest(authorization, expected):
                raise HTTPException(status_code=401, detail="Bad or missing token")

        class EmbedRequest(BaseModel):
            texts: list[str]

        @api.get("/health")
        def health():
            return {"status": "ok", "service": "auditsym-embed", "dim": EMBED_DIM}

        @api.post("/embed")
        def embed(req: EmbedRequest, authorization: str | None = Header(default=None)):
            check_auth(authorization)

            texts = req.texts or []
            if len(texts) > MAX_TEXTS:
                raise HTTPException(422, f"Too many texts (max {MAX_TEXTS})")
            if sum(len(t) for t in texts) > MAX_TOTAL_CHARS:
                raise HTTPException(422, f"Payload too large (max {MAX_TOTAL_CHARS} chars)")
            if not texts:
                return {"vectors": [], "dim": EMBED_DIM, "count": 0}

            vecs = self.model.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
            return {"vectors": vecs.tolist(), "dim": EMBED_DIM, "count": len(texts)}

        return api
