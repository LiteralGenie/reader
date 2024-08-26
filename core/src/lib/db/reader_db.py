import sqlite3
from typing import TypeAlias

from ..paths import DATA_DIR

ReaderDb: TypeAlias = sqlite3.Connection


def load_reader_db() -> ReaderDb:
    db = sqlite3.connect(DATA_DIR / "reader.sqlite")
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            version     TEXT
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id          TEXT     NOT NULL,
            type        TEXT     NOT NULL,
            data        TEXT     NOT NULL,
            processing  BOOLEAN  NOT NULL,
            progress    REAL     NOT NULL,
            result      TEXT,

            PRIMARY KEY (id, type)
        )
        """
    )

    _check_version(db)

    return db


def clear_jobs(db: ReaderDb):
    db.execute("DELETE FROM jobs")
    db.commit()


def _check_version(db: ReaderDb):
    r = db.execute("SELECT version FROM metadata").fetchone()
    if r is None:
        db.execute("INSERT INTO metadata (version) VALUES (?)", ["1"])
        db.commit()
