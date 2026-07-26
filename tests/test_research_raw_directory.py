"""Stellt sicher, dass research/raw/ ausschliesslich die absichtlich versionierte README.md
trackt (siehe .gitignore) -- keine Rohdaten (PDF, RIS, BibTeX, CSV, DOCX, ...) duerfen dort
jemals eingecheckt werden, auch nicht per `git add -f`."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_only_readme_is_tracked_under_research_raw():
    result = subprocess.run(
        ["git", "ls-files", "research/raw/"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    assert tracked == ["research/raw/README.md"], (
        f"expected only research/raw/README.md to be tracked, got: {tracked}"
    )
