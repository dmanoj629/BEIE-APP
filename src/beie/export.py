"""Project archive exporter — packages the active repository into an in-memory ZIP.

Completely portable, avoids any hardcoded user machine paths.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path


def generate_project_zip() -> bytes:
    """Generate an in-memory ZIP archive of the clean project repository."""
    buf = io.BytesIO()
    # Resolve repository root
    project_root = Path(__file__).resolve().parents[2]

    # Excluded directories and file patterns
    excluded_dirs = {
        "__pycache__",
        ".ruff_cache",
        ".pytest_cache",
        ".git",
        ".venv",
        "venv",
        "env",
        ".idea",
        ".vscode",
    }
    excluded_exts = {".pyc", ".pyo", ".zip"}

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in project_root.rglob("*"):
            if file_path.is_file():
                # Check path parts
                if any(part in excluded_dirs or part.startswith(".") for part in file_path.parts):
                    continue
                if file_path.suffix.lower() in excluded_exts:
                    continue
                # Relative path inside zip
                rel_path = file_path.relative_to(project_root)
                zf.write(file_path, arcname=str(rel_path))

    return buf.getvalue()
