"""Tests for portable project ZIP export."""

from __future__ import annotations

import io
import zipfile

from beie.export import generate_project_zip


def test_generate_project_zip_is_valid():
    zip_bytes = generate_project_zip()
    assert len(zip_bytes) > 10_000, "Exported zip is unexpectedly small."

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "requirements.txt" in namelist or any("requirements.txt" in n for n in namelist)
        assert any("src/beie/contracts.py" in n or "contracts.py" in n for n in namelist)
        assert not any("__pycache__" in n for n in namelist)
        assert not any(".git" in n for n in namelist)
