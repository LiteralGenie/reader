from itertools import chain
from pathlib import Path

from PIL import Image

from .config import Config
from .constants import SUPPORTED_IMAGE_EXTENSIONS
from .db.chapter_db import CHAPTER_DB_FILENAME, get_page, insert_page, load_chapter_db
from .db.series_db import (
    SERIES_DB_FILENAME,
    SeriesDb,
    load_series_db,
    select_series,
    update_series,
)

SERIES_COVER_FILENAME = "_reader_cover.png"


def get_all_series(cfg: Config) -> list[dict]:
    series = []

    for fp in cfg.root_image_folder.glob("*"):
        if fp.is_file():
            continue

        info = get_series(cfg, fp.name)
        info["filename"] = fp.name
        series.append(info)

    series.sort(key=lambda info: info["filename"])

    return series


def get_all_chapters(cfg: Config, series: str):
    chaps = []

    series_dir = cfg.root_image_folder / series
    if not series_dir.exists():
        raise FileNotFoundError()

    for fp in series_dir.glob("*"):
        if fp.is_file():
            continue

        chaps.append(
            dict(
                filename=fp.name,
            )
        )

    chaps.sort(key=lambda d: d["filename"])

    return chaps


def get_all_pages(cfg: Config, series: str, chapter: str):
    chap_dir = cfg.root_image_folder / series / chapter
    if not chap_dir.exists():
        raise FileNotFoundError()

    globs = [chap_dir.glob(f"*{ext}") for ext in SUPPORTED_IMAGE_EXTENSIONS]
    fp_images = list(chain(*globs))
    fp_images.sort(key=lambda fp: fp.name)

    db = load_chapter_db(chap_dir)

    pages = []
    for fp in fp_images:
        d = get_page(db, fp.name)
        if not d:
            d = insert_page(db, fp)

        pages.append(d)
    pages.sort(key=lambda d: d["filename"])

    return pages


def get_series(cfg: Config, filename: str):
    fp = cfg.root_image_folder / filename
    db = load_series_db(fp)

    info = select_series(db)
    info["filename"] = filename

    return info


def create_series(cfg: Config, filename: str, name: str) -> SeriesDb:
    series_dir = cfg.root_image_folder / filename
    series_dir.mkdir()

    db = load_series_db(series_dir)
    update_series(db, name=name)

    return db


def upsert_cover(
    cfg: Config,
    series: str,
    cover: Image.Image,
    resize=False,
):
    series_dir = cfg.root_image_folder / series
    if not series_dir.exists():
        raise FileNotFoundError()

    after_resize = cover
    if resize:
        if cfg.max_auto_cover_x > 0:
            scale_x = cover.size[0] / cfg.max_auto_cover_x
        else:
            scale_x = 1

        if cfg.max_auto_cover_y > 0:
            scale_y = cover.size[1] / cfg.max_auto_cover_y
        else:
            scale_y = 1

        scale = max(scale_x, scale_y)

        if scale > 1:
            w = int(cover.size[0] / scale)
            h = int(cover.size[1] / scale)

            after_resize = cover.resize((w, h))

    fp = series_dir / SERIES_COVER_FILENAME
    after_resize.save(fp)


def count_file_types(fp: Path):
    children = fp.glob("**/*")

    tally = dict(
        images=0,
        other=0,
        folders=0,
    )

    for fp in children:
        if fp.is_dir():
            tally["folders"] += 1
        elif fp.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            tally["images"] += 1
        elif fp.name in [
            SERIES_COVER_FILENAME,
            SERIES_DB_FILENAME,
            CHAPTER_DB_FILENAME,
        ]:
            pass
        else:
            tally["other"] += 1

    return tally
