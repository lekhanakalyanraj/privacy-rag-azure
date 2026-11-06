# The ingestion job.
#
# A job, not a service: it runs to completion and exits, so there is no server,
# no port and no health probe. Installs the `ingest` extra only - no FastAPI,
# no uvicorn.
#
# This is the one image with write access to the search index, which is exactly
# why it is a separate image with a separate identity.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --no-cache-dir \
      "pydantic>=2.9" "pydantic-settings>=2.6" \
      "azure-identity>=1.19" "azure-search-documents>=12.0" "openai>=1.57" \
      "azure-storage-blob>=12.24"

COPY libs/rag_core/src/rag_core/     /app/rag_core/
COPY services/ingest/src/rag_ingest/ /app/rag_ingest/

RUN useradd --create-home --uid 10001 appuser
USER appuser

# No arguments: the default behaviour reads the corpus from blob storage, which
# is the production behaviour, so the Container Apps Job needs no command
# override. Pass --recreate via the job's args when the schema changes.
ENTRYPOINT ["python", "-m", "rag_ingest"]
