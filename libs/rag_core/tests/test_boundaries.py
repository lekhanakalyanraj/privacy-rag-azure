"""Architectural boundaries, enforced rather than documented.

The security argument for splitting the API from the ingestion job is that the
container serving public traffic has no code path to modifying the index. That
claim is only worth making if something checks it, because the way it breaks is
someone adding a convenient import six months from now and nobody noticing.

These tests parse the source rather than importing it, so they run without
credentials and without the Azure SDKs being reachable.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

PACKAGES = {
    "rag_core": REPO_ROOT / "libs" / "rag_core" / "src" / "rag_core",
    "rag_api": REPO_ROOT / "services" / "api" / "src" / "rag_api",
    "rag_ingest": REPO_ROOT / "services" / "ingest" / "src" / "rag_ingest",
}


def imported_modules(package: Path) -> set[str]:
    """Every absolute module name imported anywhere in a package."""
    found: set[str] = set()

    for path in package.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module)

    return found


def test_packages_are_where_we_think_they_are() -> None:
    """Guards the other tests: a moved directory would make them vacuously pass."""
    for name, path in PACKAGES.items():
        assert path.is_dir(), f"{name} not found at {path}"
        assert (path / "__init__.py").is_file()


def test_api_cannot_reach_blob_storage() -> None:
    """The API has no business reading the corpus, and its image does not even
    install azure-storage-blob. Catch the import before the deploy does."""
    offenders = {m for m in imported_modules(PACKAGES["rag_api"]) if m.startswith("azure.storage")}

    assert not offenders, f"the API service must not import blob storage: {offenders}"


def test_api_cannot_reach_the_index_admin_client() -> None:
    """Index creation and deletion belong to the ingestion job."""
    api_imports = imported_modules(PACKAGES["rag_api"])
    offenders = {m for m in api_imports if "documents.indexes" in m}

    assert not offenders, f"the API service must not import the index admin surface: {offenders}"


def test_the_two_services_do_not_import_each_other() -> None:
    """They share the core library and nothing else. A direct import between
    them would mean one cannot deploy without the other."""
    api_imports = imported_modules(PACKAGES["rag_api"])
    ingest_imports = imported_modules(PACKAGES["rag_ingest"])

    assert not {m for m in api_imports if m.startswith("rag_ingest")}
    assert not {m for m in ingest_imports if m.startswith("rag_api")}


def test_core_does_not_depend_on_either_service() -> None:
    """Dependencies point inward. Core knowing about a service would make it
    impossible to deploy one without the other."""
    core_imports = imported_modules(PACKAGES["rag_core"])
    offenders = {m for m in core_imports if m.startswith(("rag_api", "rag_ingest"))}

    assert not offenders, f"the core library must not depend on a service: {offenders}"


def test_core_installs_in_both_images() -> None:
    """Both Dockerfiles must copy the shared library, or one of them ships a
    package whose imports cannot resolve."""
    for dockerfile in (
        REPO_ROOT / "services" / "api" / "Dockerfile",
        REPO_ROOT / "services" / "ingest" / "Dockerfile",
    ):
        assert "rag_core" in dockerfile.read_text(encoding="utf-8"), dockerfile


def test_api_image_does_not_install_blob_storage() -> None:
    """The boundary is enforced by image contents, not only by source imports."""
    dockerfile = (REPO_ROOT / "services" / "api" / "Dockerfile").read_text(encoding="utf-8")

    assert "azure-storage-blob" not in dockerfile
    assert "rag_ingest" not in dockerfile
