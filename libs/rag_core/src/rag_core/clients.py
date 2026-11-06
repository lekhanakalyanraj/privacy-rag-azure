"""Azure clients, in one place so the auth story is auditable.

No API keys. DefaultAzureCredential uses your `az login` locally and the
deployable's managed identity in Azure - same code path, so what you test is
what runs. Read-side only: the index admin client lives in rag_ingest, because
the API should not hold a handle that can destroy the index it reads.
"""

from functools import lru_cache

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from openai import AzureOpenAI

from .settings import get_settings

COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


@lru_cache
def credential() -> DefaultAzureCredential:
    """The one credential, shared by every client in the process."""
    settings = get_settings()
    if settings.azure_client_id:
        return DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id)
    return DefaultAzureCredential()


@lru_cache
def search_client() -> SearchClient:
    """Query the index. What this client may actually do is decided by the
    caller's identity, which is why the two deployables do not share one."""
    settings = get_settings()
    return SearchClient(
        endpoint=settings.search_endpoint,
        index_name=settings.search_index_name,
        credential=credential(),
    )


@lru_cache
def openai_client() -> AzureOpenAI:
    """Chat and embeddings, over Entra ID rather than a key."""
    settings = get_settings()
    return AzureOpenAI(
        azure_endpoint=settings.foundry_endpoint,
        azure_ad_token_provider=get_bearer_token_provider(credential(), COGNITIVE_SCOPE),
        api_version=settings.api_version,
    )
