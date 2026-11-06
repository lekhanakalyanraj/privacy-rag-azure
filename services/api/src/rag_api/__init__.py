"""The API service: retrieval and generation.

    settings.py   API-only configuration
    retrieve.py   hybrid search + semantic re-ranking
    answer.py     prompt, citation contract, abstention
    main.py       FastAPI surface

Read-only by construction: this identity holds Search Index Data *Reader*, and
the ingestion code is not in this image, so a bug here cannot touch the index.
"""

__version__ = "0.1.0"
