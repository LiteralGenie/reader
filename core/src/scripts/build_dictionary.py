import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import sqlite3

import requests
from datasets import load_dataset
from lib.db.dictionary_db import DictionaryDb
from lib.paths import DICTIONARY_FILE, RAW_DATA_DIR
from tqdm import tqdm

__all__ = []

FP_WIKTIONARY = RAW_DATA_DIR / "kaikki.org-dictionary-Korean.jsonl"


def main():
    download_wiktionary()

    db = init_db()

    export_wiktionary(db)
    export_ted_talks(db)

    build_words_examples_table(db)


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

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS examples (
            id          INTEGER     PRIMARY KEY,
            source      TEXT        NOT NULL,

            korean      TEXT        NOT NULL,
            english     TEXT        NOT NULL,

            UNIQUE (korean, english)
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS words_examples (
            word        TEXT        NOT NULL,
            id_example  INTEGER     NOT NULL,

            PRIMARY KEY (word, id_example),
            FOREIGN KEY (id_example) REFERENCES examples (id)
        )
        """
    )
    db.execute(
        "CREATE INDEX IF NOT EXISTS words_examples_word on words_examples (word)"
    )

    return db


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
    source = "wiktionary"

    if _is_done(db, source):
        print(f"Definitions from {source} already exported. Skipping.")
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
                    [source, d["word"], d["pos"], gloss],
                )

    _set_done(db, source)
    db.commit()


def export_ted_talks(db: DictionaryDb):
    source = "msarmi9_ted-talks"

    if _is_done(db, source):
        print(f"Examples from {source} already exported. Skipping.")
        return

    ds = load_dataset(
        "msarmi9/korean-english-multitarget-ted-talks-task",
        split="train",
        streaming=True,
    )
    ds_iter = tqdm(ds, desc=f"Loading examples from {source}...")
    for item in ds_iter:
        db.execute(
            """
            INSERT OR IGNORE INTO examples (
                source, korean, english
            ) VALUES (
                ?, ?, ?
            )
            """,
            [source, item["korean"], item["english"]],
        )

    _set_done(db, source)
    db.commit()


def build_words_examples_table(db: DictionaryDb):
    words = [r["word"] for r in db.execute("SELECT DISTINCT word FROM words")]

    for idx, w in tqdm(enumerate(words), desc="Analyzing examples..."):
        db.execute(
            f"""
            INSERT OR IGNORE INTO words_examples 
                ( word, id_example ) 
            SELECT 
                ?, id
            FROM examples
            WHERE korean LIKE ?
            """,
            [w, f"%{w}%"],
        )

        if idx % 1_000 == 0:
            db.commit()

    db.commit()


def _is_done(db: DictionaryDb, source: str):
    return db.execute(
        """
        SELECT done 
        FROM metadata 
        WHERE 
            source = ? 
            AND done = 1
        """,
        [source],
    ).fetchone()


def _set_done(db: DictionaryDb, source: str):
    db.execute(
        """
        INSERT OR REPLACE INTO metadata (
            source, done
        ) VALUES (
            ?, ?
        )
        """,
        [source, 1],
    )


main()
