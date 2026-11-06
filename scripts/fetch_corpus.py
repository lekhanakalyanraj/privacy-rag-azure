#!/usr/bin/env python3
"""Fetch the APP guidelines corpus and convert it to markdown.

    python scripts/fetch_corpus.py              # the [core] chapters
    python scripts/fetch_corpus.py --all        # all 18

Reads data/sample-corpus/MANIFEST.txt and writes one .md per chapter, named
after the URL's last path segment. That filename becomes doc_id, which the
golden set references in gold_doc - so renaming a file invalidates questions.

Stdlib only, on purpose: fetching the corpus should not require installing the
project. Output is deliberately plain - headings and paragraphs - because the
chunker is heading-aware and needs nothing else.

Licence and attribution: data/sample-corpus/ATTRIBUTION.md.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parents[1] / "data" / "sample-corpus"
MANIFEST = CORPUS_DIR / "MANIFEST.txt"
USER_AGENT = "privacy-rag-azure corpus fetcher (+https://github.com)"

SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "svg", "noscript"}
BLOCK_TAGS = {"p", "li", "div", "section", "article", "tr", "td", "th", "blockquote", "br"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class Extractor(HTMLParser):
    """Headings and block text out of an HTML page.

    Not a general-purpose converter. It keeps the heading hierarchy, which is
    what chunk.py splits on, and throws away everything else.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0
        self._heading: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        elif tag in HEADINGS:
            self._flush()
            self._heading = tag
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag in HEADINGS or tag in BLOCK_TAGS:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._buffer.append(data)

    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", "".join(self._buffer)).strip()
        self._buffer = []
        if not text:
            self._heading = None
            return
        if self._heading:
            level = int(self._heading[1])
            self.parts.append(f"{'#' * level} {text}")
            self._heading = None
        else:
            self.parts.append(text)

    def close(self) -> None:
        super().close()
        self._flush()

    @property
    def markdown(self) -> str:
        """Everything from the chapter's own h1 onward.

        Drops the cookie banner, the "On this page" nav and the skip link,
        which otherwise become chunks that match every query about the page
        rather than about privacy.
        """
        parts = self.parts
        for i, part in enumerate(parts):
            if part.startswith("# ") and not part.startswith("## "):
                parts = parts[i:]
                break
        return "\n\n".join(parts) + "\n"


def read_manifest(include_all: bool) -> list[str]:
    """URLs from the manifest. Without --all, stop at the [OPTIONAL] marker.

    The marker is matched exactly, not as a prefix: an earlier version used a
    plain-English sentinel that also appeared in the file's header comment, so
    parsing stopped on line 11 and returned nothing.
    """
    urls: list[str] = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line == "# [OPTIONAL]" and not include_all:
            break
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def doc_id(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Fetch all 18 chapters.")
    parser.add_argument("--force", action="store_true", help="Re-fetch files already present.")
    args = parser.parse_args()

    urls = read_manifest(args.all)
    print(f"{len(urls)} chapters -> {CORPUS_DIR}")
    written = 0

    for url in urls:
        out = CORPUS_DIR / f"{doc_id(url)}.md"
        if out.exists() and not args.force:
            print(f"  skip   {out.name}")
            continue
        try:
            extractor = Extractor()
            extractor.feed(fetch(url))
            extractor.close()
        # Broad on purpose: one unreachable chapter should not stop the rest.
        except Exception as exc:
            print(f"  FAIL   {doc_id(url)}: {exc}", file=sys.stderr)
            continue

        markdown = extractor.markdown
        # A page that yields almost nothing means the markup changed and the
        # extractor needs adjusting - better to say so than to index a stub.
        if len(markdown) < 2000:
            print(
                f"  THIN   {out.name}: {len(markdown)} chars - check the extractor",
                file=sys.stderr,
            )
        out.write_text(markdown, encoding="utf-8")
        written += 1
        print(f"  wrote  {out.name}  ({len(markdown):,} chars)")

    print(f"\n{written} written. Attribution: data/sample-corpus/ATTRIBUTION.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
