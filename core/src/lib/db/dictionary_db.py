import json
import sqlite3
import time
from typing import TypeAlias

from numpy import where

from ..paths import DICTIONARY_FILE

DictionaryDb: TypeAlias = sqlite3.Connection


def load_dictionary_db():
    assert DICTIONARY_FILE.exists()

    db = sqlite3.connect(DICTIONARY_FILE)
    db.row_factory = sqlite3.Row

    return db


def select_words(
    db: DictionaryDb,
    word: str,
    check_ending=False,
    check_verb=False,
) -> list[dict]:
    where_clause = "WHERE word = ?"
    to_check = [word]

    if check_ending:
        where_clause += " OR word = ?"
        to_check.append(f"-{word}")

    if check_verb:
        where_clause += " OR word LIKE ?"
        to_check.append(f"{word}%")

    return [
        dict(r)
        for r in db.execute(
            f"""
            SELECT word, pos, definition
            FROM definitions
            {where_clause}
            """,
            to_check,
        )
    ]


def select_examples(
    db: DictionaryDb,
    text: str,
    offset=0,
    limit=10,
) -> list[dict]:
    examples = db.execute(
        f"""
        SELECT korean, english, source
        FROM examples
        WHERE korean LIKE ?
        LIMIT ?
        OFFSET ?
        """,
        [f"%{text}%", limit, offset],
    ).fetchall()

    return [dict(r) for r in examples]


def count_examples(db: DictionaryDb, text: str) -> int:
    r = db.execute(
        f"""
        SELECT COUNT(*) count
        FROM examples
        WHERE korean LIKE ?
        """,
        [f"%{text}%"],
    ).fetchone()
    time.sleep(3)

    return r["count"]


def select_definitions(
    db: DictionaryDb,
    text: str,
    offset=0,
    limit=10,
) -> list[dict]:
    rs = db.execute(
        f"""
        SELECT word, pos, definition, source
        FROM definitions
        WHERE word LIKE ?
        LIMIT ?
        OFFSET ?
        """,
        [f"%{text}%", limit, offset],
    ).fetchall()

    return [dict(r) for r in rs]


def count_definitions(db: DictionaryDb, text: str) -> int:
    r = db.execute(
        f"""
        SELECT COUNT(*) count
        FROM definitions
        WHERE word LIKE ?
        """,
        [f"%{text}%"],
    ).fetchone()

    return r["count"]
