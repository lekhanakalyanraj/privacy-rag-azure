"""The index definition - the contract between ingestion and retrieval.

`content` gives BM25 keyword scoring and `content_vector` gives meaning-based
search; both on the same document is what makes one hybrid query possible
instead of two queries merged in application code. The semantic configuration
tells the re-ranker which fields to read - without it, query_type="semantic"
silently does nothing.

Free tier: 50 MB total. At 1536 dimensions a vector is ~6 KB, so a few hundred
chunks is comfortable. If space runs short, request 512 dimensions rather than
dropping documents.
"""

from __future__ import annotations

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

VECTOR_PROFILE = "hnsw-default"
VECTOR_ALGORITHM = "hnsw-config"
SEMANTIC_CONFIG = "semantic-default"


def build_index(name: str, dimensions: int = 1536) -> SearchIndex:
    """Return the index definition. Called by ingest.py; never at request time."""
    # The type= ignores are azure-search-documents 12.0.0 stub bugs, not usage
    # errors. warn_unused_ignores is on, so mypy flags them once stubs improve.
    fields = [
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, key=True),  # type: ignore[arg-type]
        SimpleField(
            name="doc_id",
            type=SearchFieldDataType.String,  # type: ignore[arg-type]
            filterable=True,
            facetable=True,
        ),
        SearchableField(name="doc_title", type=SearchFieldDataType.String),
        SearchableField(name="section", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source_url", type=SearchFieldDataType.String),  # type: ignore[arg-type]
        SimpleField(name="ordinal", type=SearchFieldDataType.Int32, sortable=True),  # type: ignore[arg-type]
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),  # type: ignore[operator]
            searchable=True,
            # Not retrievable: 1536 floats per hit tells the client nothing.
            hidden=True,
            vector_search_dimensions=dimensions,
            vector_search_profile_name=VECTOR_PROFILE,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=VECTOR_ALGORITHM)],
        profiles=[
            VectorSearchProfile(name=VECTOR_PROFILE, algorithm_configuration_name=VECTOR_ALGORITHM)
        ],
    )

    semantic_search = SemanticSearch(
        default_configuration_name=SEMANTIC_CONFIG,
        configurations=[
            SemanticConfiguration(
                name=SEMANTIC_CONFIG,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="doc_title"),
                    content_fields=[SemanticField(field_name="content")],
                    keywords_fields=[SemanticField(field_name="section")],
                ),
            )
        ],
    )

    return SearchIndex(
        name=name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )
