import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[1]
_src_dir = _project_root / "src"
_models_dir = _src_dir / "models"

for path in (_project_root, _src_dir, _models_dir):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
