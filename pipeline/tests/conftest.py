from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the repo root importable so `import pipeline` and `import app` both work
# whether pytest is invoked from the repo root or from backend/.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
for candidate in (REPO_ROOT, REPO_ROOT / "backend"):
    p = str(candidate)
    if p not in sys.path:
        sys.path.insert(0, p)
