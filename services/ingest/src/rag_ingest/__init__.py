"""The ingestion job: blob -> chunk -> embed -> push.

    settings.py   ingestion-only configuration
    sources.py    reading documents from blob storage or local disk
    embed.py      embedding with an on-disk cache
    pipeline.py   orchestration
    __main__.py   CLI entrypoint: python -m rag_ingest

A job, not a service: it runs for minutes on demand and exits. The only
deployable with write access to the index.
"""

__version__ = "0.1.0"
