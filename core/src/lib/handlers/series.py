from dataclasses import dataclass

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

    return chaps


def get_all_pages(cfg: Config, series: str, chapter: str):
    chap_dir = cfg.series_folder / series / chapter

    pages = [
        fp.name
        for fp in [
            *chap_dir.glob("*.jpg"),
            *chap_dir.glob("*.png"),
        ]
        if not fp.is_dir()
    ]

    return pages
