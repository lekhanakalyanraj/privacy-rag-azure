# The API service.
#
# Installs the `api` extra only, so this image contains no blob-storage client
# and no ingestion code. Combined with a read-only managed identity, that means
# the container serving public traffic has no path to modifying the index -
# enforced by what is in the image, not by anyone remembering not to call it.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first, so a source-only change does not reinstall the world.
RUN pip install --no-cache-dir \
      "pydantic>=2.9" "pydantic-settings>=2.6" \
      "azure-identity>=1.19" "azure-search-documents>=12.0" "openai>=1.57" \
      "fastapi>=0.115" "uvicorn[standard]>=0.32"

COPY libs/rag_core/src/rag_core/ /app/rag_core/
COPY services/api/src/rag_api/   /app/rag_api/

# Non-root. Container Apps does not require it, but an image that only runs as
# root is an image you cannot reuse anywhere stricter.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Single worker: at min_replicas 0 with one max replica there is nothing to gain
# from more, and each worker costs memory we are deliberately capping at 0.5Gi.
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
