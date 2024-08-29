import sqlite3
from pathlib import Path
from typing import TypeAlias

SeriesDb: TypeAlias = sqlite3.Connection

SERIES_DB_FILENAME = "_reader_series.sqlite"


def load_series_db(series_dir: Path, raise_on_missing=False) -> SeriesDb:
    fp = series_dir / SERIES_DB_FILENAME
    if raise_on_missing and not fp.exists():
        raise FileNotFoundError()

    db = sqlite3.connect(fp)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            version             TEXT        NOT NULL,
            
            name                TEXT        NOT NULL        DEFAULT '',
            autogen_cover       BOOLEAN     NOT NULL        DEFAULT 1,

            id_mangaupdates     TEXT        NOT NULL        DEFAULT '',
            id_mangadex         TEXT        NOT NULL        DEFAULT ''
        )
        """
    )

    _check_version(db)

    return db


def _check_version(db: SeriesDb):
    r = db.execute("SELECT version FROM metadata").fetchone()
    if r is None:
        db.execute(
            """
            INSERT INTO metadata (
                version
            ) VALUES (
                ?
            )
            """,
            ["1"],
        )
        db.commit()


def update_series(
    db: SeriesDb,
    name: str | None = None,
    id_mangaupdates: str | None = None,
    id_mangadex: str | None = None,
    autogen_cover: bool | None = None,
):
    targets = []
    if name is not None:
        targets.append(("name", name))
    if id_mangaupdates is not None:
        targets.append(("id_mangaupdates", id_mangaupdates))
    if id_mangadex is not None:
        targets.append(("id_mangadex", id_mangadex))
    if autogen_cover is not None:
        targets.append(("autogen_cover", autogen_cover))

    if not targets:
        return

    columns, values = zip(*targets)
    column_str = " , ".join(f"{c} = ?" for c in columns)

    db.execute(
        f"""
        UPDATE metadata
        SET {column_str}
        """,
        values,
    )

    db.commit()


def select_series(db: SeriesDb) -> dict:
    r = db.execute(
        """
        SELECT 
            name, id_mangaupdates, id_mangadex
        FROM metadata
        """
    ).fetchone()

    return dict(r)


def select_autogen_cover(db: SeriesDb):
    r = db.execute(
        """
        SELECT 
            autogen_cover
        FROM metadata
        """
    ).fetchone()

    return bool(r["autogen_cover"])


def update_autogen_cover(db: SeriesDb, autogen_cover: bool):
    db.execute(
        """
        UPDATE metadata
        SET autogen_cover = ?
        """,
        [autogen_cover],
    ).fetchone()

    db.commit()
