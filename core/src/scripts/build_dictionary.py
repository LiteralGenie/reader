import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import sqlite3

import requests
from lib.db.dictionary_db import DictionaryDb
from lib.paths import DICTIONARY_FILE, RAW_DATA_DIR
from tqdm import tqdm

__all__ = []

FP_WIKTIONARY = RAW_DATA_DIR / "kaikki.org-dictionary-Korean.jsonl"


def main():
    download_wiktionary()

    db = init_db()

    export_wiktionary(db)


def download_wiktionary():
    if FP_WIKTIONARY.exists():
        print("Raw wiktionary data already exists. Skipping download.")
        return

    print("Downloading wiktionary data...")
    url = "https://kaikki.org/dictionary/Korean/kaikki.org-dictionary-Korean.jsonl"
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(FP_WIKTIONARY, "wb") as file:
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)


def export_wiktionary(db: DictionaryDb):
    is_done = db.execute(
        """
        SELECT done FROM metadata WHERE source = 'wiktionary' AND done = 1
        """
    ).fetchone()

    if is_done:
        return

    data = [(json.loads(ln)) for ln in FP_WIKTIONARY.read_text().splitlines()]
    pbar = tqdm(data, desc="Exporting wiktionary data to SQLite...")
    for d in pbar:
        for sense in d["senses"]:
            for gloss in sense.get("glosses", []):
                db.execute(
                    """
                    INSERT OR IGNORE INTO words (
                        source, word, pos, definition
                    ) VALUES (
                        ?, ?, ?, ?
                    )
                    """,
                    ["wiktionary", d["word"], d["pos"], gloss],
                )

    db.execute(
        """
        INSERT OR REPLACE INTO metadata (
            source, done
        ) VALUES (
            ?, ?
        )
        """,
        ["wiktionary", 1],
    )

    db.commit()


def init_db():
    db = sqlite3.connect(DICTIONARY_FILE)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            source      TEXT        PRIMARY KEY,
            done        BOOLEAN     NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS words (
            id          INTEGER     PRIMARY KEY,
            source      TEXT        NOT NULL,

            word        TEXT        NOT NULL,
            pos         TEXT        NOT NULL,
            definition  TEXT        NOT NULL,

            UNIQUE (word, pos, definition)
        )
        """
    )

    db.execute("CREATE INDEX IF NOT EXISTS words_word on words (word)")

    return db


main()
