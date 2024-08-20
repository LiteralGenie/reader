from pathlib import Path

from ..chapter_db import get_ocr_data, load_chapter_db


def get_all_ocr_data(chap_dir: Path) -> dict[Path, dict | None]:
    fp_images = [
        *chap_dir.glob("*.jpg"),
        *chap_dir.glob("*.png"),
    ]

    db = load_chapter_db(chap_dir)

    data: dict[Path, dict | None] = dict()
    for fp in fp_images:
        data[fp] = get_ocr_data(db, fp.name)

    return data
