from dataclasses import dataclass

from pathvalidate import sanitize_filename

from ..config import Config


def get_all_series(cfg: Config) -> list[dict]:
    series = []

    for fp in cfg.series_folder.glob("*"):
        if fp.is_file():
            continue

        chapters = get_all_chapters(cfg, fp.name)

        series.append(
            dict(
                name=fp.name,
                chapters=chapters,
            )
        )

    series.sort(key=lambda d: d["name"])

    return series


def get_all_chapters(cfg: Config, series: str):
    chaps = []

    series_dir = cfg.series_folder / series
    if not series_dir.exists():
        raise FileExistsError()

    for fp in series_dir.glob("*"):
        if fp.is_file():
            continue

        has_ocr_data = (fp / "ocr_data.json").exists()

        pages = get_all_pages(cfg, series, fp.name)

        chaps.append(
            dict(
                name=fp.name,
                has_ocr_data=has_ocr_data,
                pages=pages,
            )
        )

    chaps.sort(key=lambda d: d["name"])

    return chaps


def get_all_pages(cfg: Config, series: str, chapter: str):
    chap_dir = cfg.series_folder / series / chapter
    if not chap_dir.exists():
        raise FileExistsError()

    pages = [
        fp.name
        for fp in [
            *chap_dir.glob("*.jpg"),
            *chap_dir.glob("*.png"),
        ]
        if not fp.is_dir()
    ]

    pages.sort()

    return pages


def get_series(cfg: Config, series: str) -> dict:
    return dict(
        name=series,
        chapters=get_all_chapters(cfg, series),
    )


def get_chapter(cfg: Config, series: str, chapter: str) -> dict:
    return dict(
        name=chapter,
        pages=get_all_pages(cfg, series, chapter),
    )
