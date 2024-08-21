import json
import sqlite3
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
            FROM words
            {where_clause}
            """,
            to_check,
        )
    ]


def select_examples(
    db: DictionaryDb,
    word: str,
) -> list[dict]:
    return [
        dict(r)
        for r in db.execute(
            f"""
            SELECT we.word, e.korean, e.english
            FROM words_examples we
            INNER JOIN examples e
                ON e.id = we.id_example
            WHERE we.word = ?
            """,
            [word],
        )
    ]
