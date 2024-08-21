import json
import sqlite3
from typing import TypeAlias

from numpy import where

from ..paths import WIKTIONARY_DB_FILE

WiktionaryDb: TypeAlias = sqlite3.Connection


def load_wiktionary_db():
    assert WIKTIONARY_DB_FILE.exists()

    db = sqlite3.connect(WIKTIONARY_DB_FILE)
    db.row_factory = sqlite3.Row

    return db


def select_exact_matches(
    db: WiktionaryDb,
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
        json.loads(r["data"])
        for r in db.execute(
            f"""
            SELECT data 
            FROM words
            {where_clause}
            """,
            to_check,
        )
    ]


def select_partial_matches(db: WiktionaryDb, word: str) -> list[dict]:
    return [
        json.loads(r["data"])
        for r in db.execute(
            """
            SELECT data 
            FROM words
            WHERE word LIKE ?
            """,
            [f"%{word}%"],
        )
    ]
