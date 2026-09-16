# AuditSym cloud deploy (Railway). Serves the static app + thin RAG orchestrator.
# No torch here — parsing and embedding run on Modal.
FROM python:3.12-slim

WORKDIR /app
COPY deploy/requirements.txt ./deploy/requirements.txt
RUN pip install --no-cache-dir -r deploy/requirements.txt

COPY . .

# Railway injects $PORT.
CMD ["sh", "-c", "uvicorn deploy.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
