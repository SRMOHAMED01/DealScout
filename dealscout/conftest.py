"""
conftest.py — align import paths so the backend (written for Docker workdir=/app,
i.e. `app.xxx` imports) is importable when pytest runs from the dealscout root.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

for p in (str(ROOT), str(BACKEND)):
    if p not in sys.path:
        sys.path.insert(0, p)
