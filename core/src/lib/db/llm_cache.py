import json
import sqlite3
from typing import TypeAlias

from ..paths import DATA_DIR

LlmCache: TypeAlias = sqlite3.Connection


def load_llm_cache() -> LlmCache:
    db = sqlite3.connect(DATA_DIR / "llm_cache.sqlite")
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS translations (
            korean      TEXT     PRIMARY KEY,
            english     TEXT     NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS best_defs (
            text        TEXT     PRIMARY KEY,
            best        TEXT     NOT NULL
        )
        """
    )

    return db


def select_translation(cache: LlmCache, korean: str) -> dict | None:
    korean = korean.strip()

    r = cache.execute(
        """
        SELECT english
        FROM translations
        WHERE korean = ?
        """,
        [korean],
    ).fetchone()

    return json.loads(r["english"]) if r else None


def insert_translation(cache: LlmCache, korean: str, english: str):
    korean = korean.strip()

    cache.execute(
        """
        INSERT INTO translations (
            korean, english
        ) VALUES (
            ?, ?
        )
        """,
        [korean, english],
    )


def select_best_defs(cache: LlmCache, text: str) -> list[list[list[int]]] | None:
    text = text.strip()

    r = cache.execute(
        """
        SELECT best
        FROM best_defs
        WHERE text = ?
        """,
        [text],
    ).fetchone()

    return json.loads(r["best"]) if r else None


def insert_best_defs(cache: LlmCache, text: str, best_defs: list[list[list[int]]]):
    text = text.strip()

    cache.execute(
        """
        INSERT INTO best_defs (
            text, best
        ) VALUES (
            ?, ?
        )
        """,
        [text, json.dumps(best_defs)],
    )
