import hashlib
import json
import sqlite3
from pathlib import Path
from typing import TypeAlias

import numpy as np
from PIL import Image

ChapterDb: TypeAlias = sqlite3.Connection


def load_chapter_db(chap_dir: Path) -> ChapterDb:
    db = sqlite3.connect(chap_dir / "_reader_data.sqlite")
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            version     TEXT     PRIMARY KEY
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            filename    TEXT     PRIMARY KEY,
            sha256      TEXT     NOT NULL,
            width       INTEGER  NOT NULL,
            height      TEXT     NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ocr_data (
            filename    TEXT     PRIMARY KEY,
            data        TEXT     NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS nlp_data (
            filename    TEXT     PRIMARY KEY,
            data        TEXT     NOT NULL
        )
        """
    )

    _check_version(db)

    return db


def get_page(db: ChapterDb, filename: str) -> dict | None:
    return db.execute(
        """
        SELECT filename, sha256, width, height
        FROM pages
        WHERE filename = ?
        """,
        [filename],
    ).fetchone()


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


def get_ocr_data(db: ChapterDb, filename: str) -> dict | None:
    r = db.execute(
        """
        SELECT filename, data
        FROM ocr_data
        WHERE filename = ?
        """,
        [filename],
    ).fetchone()

    if not r:
        return None

    return dict(
        filename=r["filename"],
        data=json.loads(r["data"]),
    )


def _check_version(db: ChapterDb):
    r = db.execute("SELECT version FROM metadata").fetchone()
    if r is None:
        db.execute("INSERT INTO metadata (version) VALUES (?)", ["1"])
        db.commit()
