import hashlib
import sqlite3
from pathlib import Path

import numpy as np
from PIL import Image


def load_db(fp: Path) -> sqlite3.Connection:
    db = sqlite3.connect(fp)
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            version     TEXT     NOT NULL
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

    return db


def get_page(db: sqlite3.Connection, filename: str) -> dict | None:
    return db.execute(
        """
        SELECT filename, sha256, width, height
        FROM pages
        WHERE filename = ?
        """,
        [filename],
    ).fetchone()


def insert_page(db: sqlite3.Connection, fp: Path) -> dict:
    im = Image.open(fp)

    arr = np.array(im).astype(np.uint8)
    sha256 = hashlib.sha256(arr.tobytes()).hexdigest()

    width, height = im.size

    data = dict(filename=fp.name, sha256=sha256, width=width, height=height)

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
