import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import sqlite3
from zipfile import ZipFile

import requests
from datasets import load_dataset
from lib.db.dictionary_db import DictionaryDb
from lib.paths import DICTIONARY_FILE, RAW_DATA_DIR
from tqdm import tqdm

__all__ = []


def main():
    db = init_db()

    export_wiktionary(db)
    export_krdict(db)

    export_ted_talks(db)
    export_subtitles(db)


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
        CREATE TABLE IF NOT EXISTS definitions (
            id          INTEGER     PRIMARY KEY,
            source      TEXT        NOT NULL,

            word        TEXT        NOT NULL,
            pos         TEXT,
            definition  TEXT        NOT NULL,

            UNIQUE (word, definition)
        )
        """
    )
    db.execute("CREATE INDEX IF NOT EXISTS definitions_word on definitions (word)")

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

    return db


def export_wiktionary(db: DictionaryDb):
    source = "wiktionary"

    fp_wiktionary = RAW_DATA_DIR / "kaikki.org-dictionary-Korean.jsonl"
    if fp_wiktionary.exists():
        print(f"Raw {source} data already exists. Skipping download.")
    else:
        print(f"Downloading {source} data...")
        _download(
            "https://kaikki.org/dictionary/Korean/kaikki.org-dictionary-Korean.jsonl",
            fp_wiktionary,
        )

    if _is_done(db, source):
        print(f"Definitions from {source} already exported. Skipping.")
        return

    data = [(json.loads(ln)) for ln in fp_wiktionary.read_text().splitlines()]
    pbar = tqdm(data, desc=f"Exporting {source} definitions to SQLite...")
    for d in pbar:
        for sense in d["senses"]:
            for gloss in sense.get("glosses", []):
                db.execute(
                    """
                    INSERT OR IGNORE INTO definitions (
                        source, word, pos, definition
                    ) VALUES (
                        ?, ?, ?, ?
                    )
                    """,
                    [source, d["word"], d["pos"], gloss],
                )

    _set_done(db, source)
    db.commit()


def export_krdict(db: DictionaryDb):
    source = "krdict"

    fp_krdict = RAW_DATA_DIR / "krdict.zip"
    if fp_krdict.exists():
        print("Raw krdict data already exists. Skipping download.")
    else:
        print("Downloading krdict data...")
        _download("https://krdict.korean.go.kr/dicBatchDownload?seq=103", fp_krdict)

    if _is_done(db, source):
        print(f"Definitions from {source} already exported. Skipping.")
        return

    data: list[dict] = []
    with ZipFile(fp_krdict) as zip:
        for info in zip.infolist():
            with zip.open(info.filename) as file:
                data.append(json.load(file))

    pbar = tqdm(data, desc=f"Exporting {source} definitions to SQLite...")
    for d in pbar:
        for lex in d["LexicalResource"]["Lexicon"]["LexicalEntry"]:
            lemmas = lex["Lemma"]
            if isinstance(lemmas, dict):
                lemmas = [lemmas]

            words = []
            for lemma in lemmas:
                if lemma["feat"]["att"] == "writtenForm":
                    words.append(lemma["feat"]["val"])
                elif lemma["feat"]["att"] == "variant":
                    words.extend(lemma["feat"]["val"].split(", "))
                else:
                    raise Exception(lemma)

            senses = lex["Sense"]
            if isinstance(senses, dict):
                senses = [senses]

            for sense in senses:
                equivalent = sense.get("Equivalent", [])
                if isinstance(equivalent, dict):
                    equivalent = [equivalent]

                for equiv in equivalent:
                    feats = {f["att"]: f["val"] for f in equiv["feat"]}
                    if feats["language"] != "영어":
                        continue

                    definitions = [feats["definition"], feats["lemma"]]

                    for w in words:
                        for defn in definitions:
                            db.execute(
                                """
                                INSERT OR IGNORE INTO definitions (
                                    source, word, pos, definition
                                ) VALUES (
                                    ?, ?, ?, ?
                                )
                                """,
                                [source, w, None, defn],
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
    ds_iter = tqdm(ds, desc=f"Loading examples from {source}...", total=166215)
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


def export_subtitles(db: DictionaryDb):
    source = "Helsinki-NLP/open_subtitles"

    if _is_done(db, source):
        print(f"Examples from {source} already exported. Skipping.")
        return

    ds = load_dataset(
        "Helsinki-NLP/open_subtitles",
        split="train",
        streaming=True,
        lang1="en",
        lang2="ko",
    )
    ds_iter = tqdm(ds, desc=f"Loading examples from {source}...", total=1_391_190)
    for item in ds_iter:
        db.execute(
            """
            INSERT OR IGNORE INTO examples (
                source, korean, english
            ) VALUES (
                ?, ?, ?
            )
            """,
            [source, item["translation"]["ko"], item["translation"]["en"]],
        )

    _set_done(db, source)
    db.commit()


def _download(url: str, fp: Path):
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(fp, "wb") as file:
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)


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
