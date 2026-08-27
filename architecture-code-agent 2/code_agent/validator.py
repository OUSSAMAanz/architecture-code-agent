"""Final deterministic checks independent of the model's claims."""

from __future__ import annotations

from pathlib import Path


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    if not (root / "README.md").is_file():
        errors.append("README.md is missing")
    manifests = [root / "requirements.txt", root / "pyproject.toml", root / "package.json"]
    if not any(path.is_file() for path in manifests):
        errors.append("No dependency manifest was generated")
    test_files = (
        [path for path in (root / "tests").rglob("*") if path.is_file()]
        if (root / "tests").is_dir()
        else []
    )
    if not test_files:
        errors.append("No automated tests were generated")
    source_roots = [root / "src", root / "app", root / "lib"]
    if not any(path.is_dir() and any(path.rglob("*")) for path in source_roots):
        errors.append("No source directory was generated")
    empty_files = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() and path.stat().st_size == 0]
    if empty_files:
        errors.append("Empty generated files: " + ", ".join(empty_files))
    return errors
