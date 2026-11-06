from pathlib import Path

from rag_ingest.sources import from_local


def test_from_local_reads_markdown_and_text(tmp_path: Path) -> None:
    (tmp_path / "one.md").write_text("# First Doc\n\nBody text.", encoding="utf-8")
    (tmp_path / "two.txt").write_text("plain text", encoding="utf-8")
    (tmp_path / "ignore.pdf").write_bytes(b"%PDF-1.4")

    documents = from_local(tmp_path)

    assert [d.doc_id for d in documents] == ["one", "two"]


def test_title_comes_from_the_first_heading(tmp_path: Path) -> None:
    (tmp_path / "doc.md").write_text("# Privacy Principles\n\nBody.", encoding="utf-8")

    assert from_local(tmp_path)[0].title == "Privacy Principles"


def test_title_falls_back_to_the_filename(tmp_path: Path) -> None:
    (tmp_path / "untitled.txt").write_text("no heading here", encoding="utf-8")

    assert from_local(tmp_path)[0].title == "no heading here"


def test_doc_ids_are_stable_across_reads(tmp_path: Path) -> None:
    """The golden set references doc_id, so this must not depend on walk order."""
    for name in ("b.md", "a.md", "c.md"):
        (tmp_path / name).write_text(f"# {name}\n\nbody", encoding="utf-8")

    first = [d.doc_id for d in from_local(tmp_path)]
    second = [d.doc_id for d in from_local(tmp_path)]

    assert first == second == ["a", "b", "c"]
