"""Configuration shared by both deployables.

Nothing here is secret: endpoints and deployment names get you nothing without
an Entra ID token. Each service extends CoreSettings with its own fields, so a
missing API-only variable fails in the API rather than defaulting in the job.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    """Where Search and Foundry are, and who we are when we call them."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Azure AI Search ---
    search_endpoint: str
    search_index_name: str = "corpus-v1"

    # --- Microsoft Foundry ---
    foundry_endpoint: str
    api_version: str = "2024-10-21"

    # Shared so the two sides cannot drift: a query vector from a different
    # model or dimensionality is meaningless against the index.
    embedding_deployment: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Set by Terraform; empty locally, where your az login is used. The API and
    # the job get *different* identities, so this differs between them.
    azure_client_id: str = ""


@lru_cache
def get_settings() -> CoreSettings:
    return CoreSettings()  # type: ignore[call-arg]
