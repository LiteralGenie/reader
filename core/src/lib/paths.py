from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent.parent.parent

DATA_DIR = PROJ_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

DICTIONARY_FILE = DATA_DIR / "dictionary.sqlite"

for dir in [DATA_DIR, RAW_DATA_DIR]:
    dir.mkdir(exist_ok=True)
