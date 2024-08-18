import json

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
        raise FileNotFoundError()

    for fp in series_dir.glob("*"):
        if fp.is_file():
            continue

        has_ocr_data = (fp / "ocr_data.json").exists()
        if not has_ocr_data:
            continue

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
        raise FileNotFoundError()

    fp_ocr_data = chap_dir / "ocr_data.json"
    if not fp_ocr_data.exists():
        raise FileNotFoundError()

    ocr_data = json.loads(fp_ocr_data.read_text())

    fp_images = [
        *chap_dir.glob("*.jpg"),
        *chap_dir.glob("*.png"),
    ]
    fp_images.sort(key=lambda fp: fp.name)

    pages = []
    for fp in fp_images:
        matches = ocr_data.get(fp.name, dict()).get("matches", None)
        if not matches:
            print(f"Warning: No OCR data for page {fp.name}")

        pages.append(
            dict(
                filename=fp.name,
                matches=matches,
            )
        )

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
