from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent.parent.parent

DATA_DIR = PROJ_DIR / "data"

DICTIONARY_DIR = DATA_DIR / "dictionaries"

WIKTIONARY_DB_FILE = DICTIONARY_DIR / "kaikki.org-dictionary-Korean.sqlite"

for dir in [DATA_DIR, DICTIONARY_DIR]:
    dir.mkdir(exist_ok=True)
