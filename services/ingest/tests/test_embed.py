from pathlib import Path

import pytest

from rag_ingest import embed


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Never touch the real .cache/ during tests."""
    cache = tmp_path / "embeddings"
    monkeypatch.setattr(embed, "CACHE_DIR", cache)
    return cache


def test_cache_key_depends_on_dimensions() -> None:
    """The same text at 512 and 1536 dimensions are different vectors; mixing
    them in one index is a silent failure, so the key must separate them."""
    a = embed.cache_key("hello", "text-embedding-3-small", 512)
    b = embed.cache_key("hello", "text-embedding-3-small", 1536)

    assert a != b


def test_cache_key_depends_on_model() -> None:
    a = embed.cache_key("hello", "text-embedding-3-small", 1536)
    b = embed.cache_key("hello", "some-other-model", 1536)

    assert a != b


def test_cache_round_trip() -> None:
    key = embed.cache_key("hello", "m", 3)
    assert embed.read_cached(key) is None

    embed.write_cached(key, [0.1, 0.2, 0.3])

    assert embed.read_cached(key) == [0.1, 0.2, 0.3]


def test_unreadable_cache_entry_is_discarded_not_raised(isolated_cache: Path) -> None:
    """A truncated cache file should cost one re-embed, not a crashed run."""
    key = embed.cache_key("hello", "m", 3)
    isolated_cache.mkdir(parents=True, exist_ok=True)
    (isolated_cache / f"{key}.json").write_text("{ truncated")

    assert embed.read_cached(key) is None
