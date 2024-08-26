from PIL import Image

from .config import Config
from .db.chapter_db import get_page, insert_page, load_chapter_db
from .db.series_db import SeriesDb, load_series_db, select_series, update_series

SERIES_COVER_FILENAME = "_reader_cover.png"


def get_all_series(cfg: Config) -> list[dict]:
    series = []

    for fp in cfg.series_folder.glob("*"):
        if fp.is_file():
            continue

        info = get_series(cfg, fp.name)
        info["filename"] = fp.name
        series.append(info)

    series.sort(key=lambda info: info["filename"])

    return series


def get_all_chapters(cfg: Config, series: str):
    chaps = []

    series_dir = cfg.series_folder / series
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
    chap_dir = cfg.series_folder / series / chapter
    if not chap_dir.exists():
        raise FileNotFoundError()

    fp_images = [
        *chap_dir.glob("*.jpg"),
        *chap_dir.glob("*.png"),
    ]
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
    fp = cfg.series_folder / filename
    db = load_series_db(fp)

    info = select_series(db)
    info["filename"] = filename

    return info


def create_series(cfg: Config, filename: str, name: str) -> SeriesDb:
    series_dir = cfg.series_folder / filename
    series_dir.mkdir()

    db = load_series_db(series_dir)
    update_series(db, name=name)

    return db


def upsert_cover(cfg: Config, series: str, cover: Image.Image):
    series_dir = cfg.series_folder / series
    if not series_dir.exists():
        raise FileNotFoundError()

    fp = series_dir / SERIES_COVER_FILENAME
    cover.save(fp)
