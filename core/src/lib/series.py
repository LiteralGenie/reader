import shutil
from itertools import chain
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from .config import Config
from .constants import SUPPORTED_IMAGE_EXTENSIONS
from .db.chapter_db import (
    CHAPTER_DB_FILENAME,
    ChapterDb,
    insert_page,
    load_chapter_db,
    select_chapter,
    select_page,
)
from .db.series_db import (
    SERIES_DB_FILENAME,
    SeriesDb,
    load_series_db,
    select_autogen_cover,
    select_series,
    update_autogen_cover,
    update_series,
)

SERIES_COVER_FILENAME = "_reader_cover.png"
SERIES_COVER_ALTERNATIVES = ["cover.png", "cover.jpg", "cover.jpeg"]


def get_series(cfg: Config, filename: str):
    fp = cfg.root_image_folder / filename
    if not fp.exists():
        raise FileNotFoundError()

    db = load_series_db(fp)

    info = select_series(db)
    info["filename"] = filename

    info["cover"] = None
    if not info["hide_cover"] and (cover := get_cover(cfg, filename)):
        cache_buster = cover.stat().st_mtime
        info["cover"] = f"{cover.name}?t={cache_buster}"

    chapters = get_all_chapters(cfg, filename)
    info["num_chapters"] = len(chapters)

    return info


def create_series(
    cfg: Config,
    filename: str,
    name: str,
    id_mangadex: str | None = None,
    id_mangaupdates: str | None = None,
    autogen_cover: bool | None = None,
) -> SeriesDb:
    series_dir = cfg.root_image_folder / filename
    series_dir.mkdir()

    db = load_series_db(series_dir)
    update_series(
        db,
        name=name,
        id_mangadex=id_mangadex,
        id_mangaupdates=id_mangaupdates,
        autogen_cover=autogen_cover,
    )

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

    if resize:
        scale = 1
        if cfg.max_auto_cover_x > 0:
            scale = cover.size[0] / cfg.max_auto_cover_x

        if scale > 1:
            w = int(cover.size[0] / scale)
            h = int(cover.size[1] / scale)

            cover = cover.resize((w, h))

        if cfg.max_auto_cover_y > 0:
            if cover.size[1] > cfg.max_auto_cover_y:
                cover = cover.crop((0, 0, cover.size[0], cfg.max_auto_cover_y))

    fp = series_dir / SERIES_COVER_FILENAME
    cover.save(fp)

    return fp


def get_chapter(cfg: Config, series: str, chapter: str):
    fp = cfg.root_image_folder / series / chapter
    db = load_chapter_db(fp)

    info = select_chapter(db)
    info["filename"] = chapter

    pages = get_all_pages(cfg, series, chapter)
    info["num_pages"] = len(pages)

    return info


def get_all_series(cfg: Config) -> list[dict]:
    series = []

    for fp in cfg.root_image_folder.glob("*"):
        if fp.is_file():
            continue

        info = get_series(cfg, fp.name)
        info["filename"] = fp.name
        series.append(info)

    series.sort(key=lambda info: info["name"].lower() or info["filename"].lower())

    return series


def get_all_chapters(cfg: Config, series: str):
    chaps = []

    series_dir = cfg.root_image_folder / series
    if not series_dir.exists():
        raise FileNotFoundError()

    for fp in series_dir.glob("*"):
        if fp.is_file():
            continue

        info = get_chapter(cfg, series, fp.name)
        chaps.append(info)

    chaps.sort(key=lambda info: info["name"].lower() or info["filename"].lower())

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
        d = select_page(db, fp.name)
        if not d:
            d = insert_page(db, fp)

        d["size"] = fp.stat().st_size

        pages.append(d)
    pages.sort(key=lambda d: d["filename"].lower())

    return pages


def count_file_types(fp: Path):
    children = fp.glob("**/*")

    tally = dict(
        images=0,
        other=0,
        folders=1,
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


def raise_on_size_limit(files: list[UploadFile], max_bytes: int):
    sizes = []
    for f in files:
        if not f.size:
            raise HTTPException(411)

        sizes.append(f.size)

    total = sum(sizes)
    if total > max_bytes:
        raise HTTPException(413, "Image too large")


def get_cover(cfg: Config, series: str):
    series_dir = cfg.root_image_folder / series
    db = load_series_db(series_dir, raise_on_missing=True)

    if select_autogen_cover(db):
        chaps = get_all_chapters(cfg, series)

        for ch in chaps:
            pages = get_all_pages(cfg, series, ch["filename"])
            if not pages:
                continue

            fp = series_dir / ch["filename"] / pages[0]["filename"]
            im = Image.open(fp)
            upsert_cover(cfg, series, im, resize=True)

            update_autogen_cover(db, False)

    for filename in [SERIES_COVER_FILENAME] + SERIES_COVER_ALTERNATIVES:
        fp = series_dir / filename
        if fp.exists():
            return fp


def validate_image_upload(
    upload: UploadFile,
    max_bytes: int | None,
) -> Image.Image:
    if max_bytes:
        raise_on_size_limit([upload], max_bytes)

    try:
        im = Image.open(upload.file)
        im.copy().verify()
    except:
        print("here")
        raise HTTPException(400, "Invalid image file")

    return im


def apply_chapter_crud(
    db: ChapterDb,
    to_delete: set[Path],
    to_rename: dict[Path, Path],
    to_add: list[dict],
    name: str | None = None,
):
    after_delete: dict[Path, Path] = dict()
    after_rename: dict[Path, Path] = dict()
    after_add: list[Path] = []

    try:
        for fp in to_delete:
            fp_temp = _get_temp_file(fp)
            after_delete[fp] = fp_temp
            shutil.move(fp, fp_temp)

            db.execute("DELETE FROM pages WHERE filename = ?", [fp.name])
            db.execute("DELETE FROM ocr_data WHERE filename = ?", [fp.name])

        for fp_before, fp_after in to_rename.items():
            fp_target_before = after_rename.get(fp_before, _get_temp_file(fp_before))
            if not fp_target_before.exists():
                assert fp_before.exists()
                after_rename[fp_before] = fp_target_before
                shutil.move(fp_before, fp_target_before)

            db.execute(
                "UPDATE pages SET filename = ? WHERE filename = ?",
                [fp_target_before.name, fp_before.name],
            )
            db.execute(
                "UPDATE ocr_data SET filename = ? WHERE filename = ?",
                [fp_target_before.name, fp_before.name],
            )

            fp_target_after = fp_after
            if fp_target_after.exists():
                fp_temp_after = _get_temp_file(fp_after)
                after_rename[fp_after] = fp_temp_after
                shutil.move(fp_after, fp_temp_after)

            db.execute(
                "UPDATE pages SET filename = ? WHERE filename = ?",
                [fp_target_after.name, fp_after.name],
            )
            db.execute(
                "UPDATE ocr_data SET filename = ? WHERE filename = ?",
                [fp_target_after.name, fp_after.name],
            )

            shutil.copy(fp_target_before, fp_target_after)
            db.execute(
                "UPDATE pages SET filename = ? WHERE filename = ?",
                [fp_target_before.name, fp_target_after.name],
            )
            db.execute(
                "UPDATE ocr_data SET filename = ? WHERE filename = ?",
                [fp_target_before.name, fp_target_after.name],
            )

        for d in to_add:
            after_add.append(d["fp"])
            d["im"].save(d["fp"])

        if name:
            db.execute("UPDATE metadata SET name = ?", [name])

        for fp in after_delete.values():
            fp.unlink()
        for fp in after_rename.values():
            fp.unlink()
            db.execute("DELETE FROM pages WHERE filename = ?", [fp.name])
            db.execute("DELETE FROM ocr_data WHERE filename = ?", [fp.name])

        db.commit()

    except:
        for fp_before, fp_after in after_delete.items():
            if fp_after.exists():
                shutil.move(fp_after, fp_before)

        for fp_before, fp_after in after_delete.items():
            if fp_after.exists():
                shutil.move(fp_after, fp_before)

        for fp in after_add:
            if fp.exists():
                fp.unlink()

        db.rollback()

        raise


def _get_temp_file(fp: Path):
    idx = 1
    fp_temp = None
    while not fp_temp or fp_temp.exists():
        fp_temp = fp.parent / (fp.name + f".tmp.{idx}")
        idx += 1

    return fp_temp
