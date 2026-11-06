from rag_core.chunk import chunk_document, estimate_tokens, split_sections


def test_split_sections_finds_each_heading(sample_markdown: str) -> None:
    sections = split_sections(sample_markdown)
    titles = [title for title, _ in sections]

    assert "APP 7 Direct marketing" in titles
    assert "APP 8 Cross-border disclosure" in titles


def test_split_sections_keeps_preamble_without_heading() -> None:
    sections = split_sections("Loose text with no heading at all.")
    assert sections == [("", "Loose text with no heading at all.")]


def test_chunks_never_span_two_sections(sample_markdown: str) -> None:
    """The core invariant. A chunk that mixes sections produces citations that
    point at the wrong heading, which is worse than no citation."""
    chunks = chunk_document(
        doc_id="privacy", doc_title="Privacy Principles", markdown=sample_markdown
    )

    for chunk in chunks:
        if chunk.section:
            assert chunk.section in chunk.text


def test_chunk_ids_are_deterministic(sample_markdown: str) -> None:
    """Re-running ingestion on unchanged input must not invalidate citations or
    make two eval runs incomparable."""
    first = chunk_document(doc_id="d", doc_title="T", markdown=sample_markdown)
    second = chunk_document(doc_id="d", doc_title="T", markdown=sample_markdown)

    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]


def test_chunk_ids_are_unique(sample_markdown: str) -> None:
    chunks = chunk_document(doc_id="d", doc_title="T", markdown=sample_markdown)
    ids = [c.chunk_id for c in chunks]

    assert len(ids) == len(set(ids))


def test_small_target_produces_more_chunks(sample_markdown: str) -> None:
    """Sanity check on the knob you will actually tune on Saturday."""
    coarse = chunk_document(doc_id="d", doc_title="T", markdown=sample_markdown, target_tokens=2000)
    fine = chunk_document(doc_id="d", doc_title="T", markdown=sample_markdown, target_tokens=20)

    assert len(fine) >= len(coarse)


def test_estimate_tokens_is_never_zero() -> None:
    assert estimate_tokens("") == 1
    assert estimate_tokens("a" * 400) > 50
