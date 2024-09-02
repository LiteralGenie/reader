import sqlite3
import time
from typing import TypeAlias

from ..misc_utils import to_jamo, to_joined_jamo
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
    check_dash_prefix=False,
    check_suffix=False,
) -> list[dict]:
    where_clause = "jamo = ?"
    to_check = [to_joined_jamo(word)]

    if check_dash_prefix:
        where_clause += " OR jamo = ?"
        to_check.append(f"-{to_joined_jamo(word)}")

    if check_suffix:
        where_clause += " OR jamo LIKE ?"
        to_check.append(f"{to_joined_jamo(word)}%")

    return [
        dict(r)
        for r in db.execute(
            f"""
            SELECT id, word, pos, definition
            FROM definitions
            WHERE 
                ({where_clause})

                -- wiktionary quirk
                AND definition NOT LIKE 'See the entry%'

                AND pos != 'syllable'
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
        WHERE jamo LIKE ?
        LIMIT ?
        OFFSET ?
        """,
        [f"%{to_joined_jamo(text)}%", limit, offset],
    ).fetchall()

    return [dict(r) for r in examples]


def count_examples(db: DictionaryDb, text: str) -> int:
    r = db.execute(
        f"""
        SELECT COUNT(*) count
        FROM examples
        WHERE jamo LIKE ?
        """,
        [f"%{to_joined_jamo(text)}%"],
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
        SELECT id, word, pos, definition, source
        FROM definitions
        WHERE 
            jamo LIKE ?
            AND definition NOT LIKE 'See the entry%'
            AND pos != 'syllable'
        LIMIT ?
        OFFSET ?
        """,
        [f"%{to_joined_jamo(text)}%", limit, offset],
    ).fetchall()

    return [dict(r) for r in rs]


def count_definitions(db: DictionaryDb, text: str) -> int:
    r = db.execute(
        f"""
        SELECT COUNT(*) count
        FROM definitions
        WHERE 
            jamo LIKE ?
            AND definition NOT LIKE 'See the entry%'
            AND pos != 'syllable'
        """,
        [f"%{to_joined_jamo(text)}%"],
    ).fetchone()

    return r["count"]
