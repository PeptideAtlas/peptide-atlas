"""Pytest-Konfiguration: macht tools/ als importierbares Modulverzeichnis verfuegbar.

Die Tools unter tools/ sind bewusst einfache Skripte ohne eigenes Package-Setup
(siehe Abschnitt "Static-First" / "keine unnoetige Abstraktion"). Fuer Tests
wird das Verzeichnis daher direkt in sys.path aufgenommen.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

for path in (str(REPO_ROOT), str(TOOLS_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)
