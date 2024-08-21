import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import sqlite3

import requests
from lib.paths import DATA_DIR, WIKTIONARY_DB_FILE
from tqdm import tqdm

__all__ = []

FP_RAW = DATA_DIR / "dictionaries" / "kaikki.org-dictionary-Korean.jsonl"


def main():
    download()
    export_to_sqlite()


def download():
    if FP_RAW.exists():
        print("Raw data already exists. Skipping download.")
        return

    print("Downloading wiktionary data...")
    url = "https://kaikki.org/dictionary/Korean/kaikki.org-dictionary-Korean.jsonl"
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(FP_RAW, "wb") as file:
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)


def export_to_sqlite():
    if WIKTIONARY_DB_FILE.exists():
        print("Database already exists. All done.")
        return

    db = init_db()

    data = [
        (
            json.loads(ln),
            ln,
        )
        for ln in FP_RAW.read_text().splitlines()
    ]

    for d, raw in tqdm(data, desc="Exporting to SQLite..."):
        db.execute(
            """
            INSERT INTO words (
                word, data
            ) VALUES (
                ?, ?
            )
            """,
            [d["word"], raw],
        )

    db.commit()


def init_db():
    db = sqlite3.connect(WIKTIONARY_DB_FILE)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS words (
            id      INTEGER     PRIMARY KEY,

            word    TEXT        NOT NULL,
            data    TEXT        NOT NULL 
        )
        """
    )

    db.execute("CREATE INDEX words_word on words (word)")

    return db


main()
