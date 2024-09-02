import hashlib
import sqlite3
from pathlib import Path
from typing import TypeAlias
from uuid import uuid4

import numpy as np
from comic_ocr.lib.label_utils import StitchedBlock
from PIL import Image

ChapterDb: TypeAlias = sqlite3.Connection

CHAPTER_DB_FILENAME = "_reader_chapter.sqlite"


def load_chapter_db(chap_dir: Path, raise_on_missing=False) -> ChapterDb:
    fp = chap_dir / CHAPTER_DB_FILENAME
    if raise_on_missing and not fp.exists():
        raise FileNotFoundError()

    db = sqlite3.connect(fp)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            version     TEXT,
            name        TEXT        NOT NULL    DEFAULT ''
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            filename    TEXT     PRIMARY KEY,
            sha256      TEXT     NOT NULL,
            width       INTEGER  NOT NULL,
            height      TEXT     NOT NULL,
            done_ocr    BOOLEAN  NOT NULL   DEFAULT 0
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ocr_data (
            id          TEXT        PRIMARY KEY,

            filename    TEXT        NOT NULL,
            value       TEXT        NOT NULL,
            confidence  TEXT        NOT NULL,
            x1          INTEGER     NOT NULL,
            x2          INTEGER     NOT NULL,
            y1          INTEGER     NOT NULL,
            y2          INTEGER     NOT NULL
        )
        """
    )

    _check_version(db)

    return db


def select_page(db: ChapterDb, filename: str) -> dict | None:
    r = db.execute(
        """
        SELECT filename, sha256, width, height
        FROM pages
        WHERE filename = ?
        """,
        [filename],
    ).fetchone()

    return dict(r) if r else None


def insert_page(db: ChapterDb, fp: Path) -> dict:
    im = Image.open(fp)

    arr = np.array(im).astype(np.uint8)
    sha256 = hashlib.sha256(arr.tobytes()).hexdigest()

    width, height = im.size

    data = dict(
        filename=fp.name,
        sha256=sha256,
        width=width,
        height=height,
    )

    db.execute(
        """
        INSERT OR IGNORE into pages (
            filename,   sha256,   width,    height
        ) VALUES (
            :filename,  :sha256,  :width,   :height
        )
        """,
        data,
    )
    db.commit()

    return data


def select_ocr_data(db: ChapterDb, filename: str) -> dict | None:
    page_data = db.execute(
        """
        SELECT done_ocr
        FROM pages
        WHERE filename = ?
        """,
        [filename],
    ).fetchone()

    if not page_data or not page_data["done_ocr"]:
        return None

    rs = db.execute(
        """
        SELECT id, value, confidence, x1, x2, y1, y2
        FROM ocr_data
        WHERE filename = ?
        """,
        [filename],
    ).fetchall()

    return {
        r["id"]: dict(
            id=r["id"],
            value=r["value"],
            confidence=r["confidence"],
            bbox=[r["y1"], r["x1"], r["y2"], r["x2"]],
        )
        for r in rs
    }


def insert_ocr_data(db: ChapterDb, filename: str, block: StitchedBlock) -> dict | None:
    id = uuid4().hex
    value = block.value.replace("\n", " ")
    y1, x1, y2, x2 = block.bbox

    r = db.execute(
        """
        INSERT INTO ocr_data (
            id, filename, value, confidence, x1, x2, y1, y2
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ? 
        )
        """,
        [id, filename, value, block.confidence, x1, x2, y1, y2],
    ).fetchone()


def update_ocr_text(db: ChapterDb, id: str, value: str) -> dict | None:
    db.execute(
        """
        UPDATE ocr_data
        SET value = ?
        WHERE id = ?
        """,
        [value, id],
    ).fetchone()

    db.commit()


def delete_ocr_data(db: ChapterDb, id: str) -> dict | None:
    db.execute(
        """
        DELETE FROM ocr_data
        WHERE id = ?
        """,
        [id],
    ).fetchone()

    db.commit()


def _check_version(db: ChapterDb):
    r = db.execute("SELECT version FROM metadata").fetchone()
    if r is None:
        db.execute("INSERT INTO metadata (version) VALUES (?)", ["1"])
        db.commit()


def update_chapter(
    db: ChapterDb,
    name: str,
):
    db.execute(
        f"""
        UPDATE metadata
        SET name = ?
        """,
        [name],
    )

    db.commit()


def select_chapter(db: ChapterDb) -> dict:
    r = db.execute(
        """
        SELECT 
            name
        FROM metadata
        """
    ).fetchone()

    return dict(r)
