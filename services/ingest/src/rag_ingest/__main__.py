"""CLI entrypoint.

    python -m rag_ingest --local data/sample-corpus --recreate   # development
    python -m rag_ingest                                         # blob storage

The image runs the second form, so the job needs no command override: the
default behaviour is the production behaviour.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rag_ingest",
        description="Chunk, embed and push the corpus into Azure AI Search.",
    )
    parser.add_argument(
        "--local",
        type=Path,
        help="Read documents from this directory instead of blob storage.",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and rebuild the index. Required after changing the schema "
        "or the embedding dimensionality.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    pipeline.run(local_path=args.local, recreate=args.recreate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
