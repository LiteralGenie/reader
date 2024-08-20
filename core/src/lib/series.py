from .chapter_db import get_page, insert_page, load_chapter_db
from .config import Config


def get_all_series(cfg: Config) -> list[dict]:
    series = []

    for fp in cfg.series_folder.glob("*"):
        if fp.is_file():
            continue

        series.append(
            dict(
                filename=fp.name,
            )
        )

    series.sort(key=lambda d: d["filename"])

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
