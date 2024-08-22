import sqlite3
from typing import TypeAlias

from ..paths import DATA_DIR

MtlCache: TypeAlias = sqlite3.Connection


def load_mtl_cache() -> MtlCache:
    db = sqlite3.connect(DATA_DIR / "mtl_cache.sqlite")
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS translations (
            korean      TEXT     PRIMARY KEY,
            english     TEXT     NOT NULL
        )
        """
    )

    return db


def select_translation(cache: MtlCache, korean: str) -> str | None:
    r = cache.execute(
        "SELECT english FROM translations WHERE korean = ?",
        [korean.strip()],
    ).fetchone()

    return r["english"] if r else None


def insert_translation(cache: MtlCache, korean: str, english: str):
    cache.execute(
        """
        INSERT INTO translations (
            korean, english
        ) VALUES (
            ?, ?
        )
        """,
        [korean.strip(), english.strip()],
    )
