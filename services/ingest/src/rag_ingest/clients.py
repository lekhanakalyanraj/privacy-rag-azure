"""Clients the API deliberately does not have: the index admin client, which
can rebuild and delete the index, and the blob client. The API image does not
even install azure-storage-blob, so the boundary is enforced by image contents
rather than by anyone remembering. test_boundaries.py checks it.
"""

from functools import lru_cache

from azure.search.documents.indexes import SearchIndexClient
from azure.storage.blob import BlobServiceClient

from rag_core.clients import credential

from .settings import get_settings


@lru_cache
def index_admin_client() -> SearchIndexClient:
    """Creates and rebuilds the index - the dangerous handle."""
    return SearchIndexClient(
        endpoint=get_settings().search_endpoint,
        credential=credential(),
    )


@lru_cache
def blob_client() -> BlobServiceClient:
    """Reads the source corpus."""
    return BlobServiceClient(
        account_url=get_settings().blob_endpoint,
        credential=credential(),
    )
