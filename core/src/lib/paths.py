from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent.parent.parent

DATA_DIR = PROJ_DIR / "data"

for dir in [DATA_DIR]:
    dir.mkdir(exist_ok=True)
