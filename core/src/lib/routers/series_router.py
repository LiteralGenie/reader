import shutil
import traceback
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from pydantic import BaseModel

from ..config import Config
from ..db.chapter_db import load_chapter_db, update_chapter
from ..db.series_db import load_series_db, update_series
from ..misc_utils import sanitize_or_raise_400
from ..series import (
    count_file_types,
    create_series,
    get_all_chapters,
    get_all_pages,
    get_all_series,
    get_chapter,
    get_series,
    upsert_cover,
)

router = APIRouter()


@router.get("/series")
def series(req: Request):
    data = get_all_series(req.app.state.cfg)
    return data


@router.get("/series/{series}")
def series_by_id(req: Request, series: str):
    series = sanitize_or_raise_400(series)

    try:
        data = get_series(req.app.state.cfg, series)
        data["chapters"] = get_all_chapters(req.app.state.cfg, series)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@router.get("/series/{series}/{chapter}")
def chapter_by_id(req: Request, series: str, chapter: str):
    series = sanitize_or_raise_400(series)
    chapter = sanitize_or_raise_400(chapter)

    try:
        data = get_all_pages(req.app.state.cfg, series, chapter)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@router.get("/series/{series}/{chapter}/{page}")
def image_by_id(req: Request, series: str, chapter: str, page: str):
    series = sanitize_or_raise_400(series)
    chapter = sanitize_or_raise_400(chapter)
    page = sanitize_or_raise_400(page)

    fp: Path = req.app.state.cfg.root_image_folder / series / chapter / page
    if not fp.exists():
        raise HTTPException(404)

    return FileResponse(fp)


class CreateSeriesRequest(BaseModel):
    filename: str
    name: str


@router.post("/series")
def create_series_(req: Request, body: CreateSeriesRequest):
    filename = sanitize_or_raise_400(body.filename)

    if "" in [filename]:
        raise HTTPException(400)

    try:
        create_series(req.app.state.cfg, filename, body.name)
    except FileExistsError:
        raise HTTPException(400)

    return get_series(req.app.state.cfg, filename)


@router.patch("/cover/{series}")
def upsert_series_cover(req: Request, series: str, cover: UploadFile):
    series = sanitize_or_raise_400(series)

    try:
        im = Image.open(cover.file)
        im.verify()
    except:
        raise HTTPException(400)

    try:
        upsert_cover(req.app.state.cfg, series, im)
    except FileNotFoundError:
        raise HTTPException(404)

    return "ok"


@router.patch("/cover/{series}/auto")
def upsert_series_cover_auto(req: Request, series: str):
    cfg: Config = req.app.state.cfg
    series = sanitize_or_raise_400(series)

    try:
        fp_im = None
        for ch in get_all_chapters(cfg, series):
            pages = get_all_pages(cfg, series, ch["filename"])
            fp_im = pages[0]["filename"]
            break

        if fp_im:
            im = Image.open(fp_im)
            upsert_cover(cfg, series, im, resize=True)
    except FileNotFoundError:
        raise HTTPException(404)

    return "ok"


class UpdateSeriesRequest(BaseModel):
    filename: str
    name: str | None
    id_mangaupdates: str | None
    id_mangadex: str | None


@router.post("/series/{series}")
def update_series_(req: Request, body: UpdateSeriesRequest):
    filename = sanitize_or_raise_400(body.filename)

    try:
        series_dir = req.app.state.cfg.root_image_folder / filename
        db = load_series_db(series_dir, raise_on_missing=True)
    except FileNotFoundError:
        raise HTTPException(404)

    update_series(
        db,
        body.name,
        body.id_mangaupdates,
        body.id_mangadex,
    )

    info = get_series(req.app.state.cfg, filename)
    return info


class DeleteSeriesRequest(BaseModel):
    series: str


@router.delete("/series")
def delete_series_(req: Request, body: DeleteSeriesRequest):
    filename = sanitize_or_raise_400(body.series)

    series_dir = req.app.state.cfg.root_image_folder / filename
    if not series_dir.exists():
        raise HTTPException(404)

    try:
        shutil.rmtree(series_dir)
    except:
        traceback.print_exc()
        raise HTTPException(500)

    return "ok"


@router.post("/chapter/{series}/{chapter}")
def create_chapter(
    req: Request,
    series: str,
    chapter: str,
    pages: list[UploadFile],
):
    series = sanitize_or_raise_400(series)
    chapter_filename = sanitize_or_raise_400(chapter)

    cfg: Config = req.app.state.cfg

    series_dir = cfg.root_image_folder / series
    if not series_dir.exists():
        raise HTTPException(404)

    chap_dir = series_dir / chapter_filename
    if chap_dir.exists():
        raise HTTPException(400)

    to_create = []
    names_used = set()
    default_name = 1
    for pg in pages:
        try:
            im = Image.open(pg.file)
            im.verify()

            filename = None
            if pg.filename:
                filename = pg.filename.split(".")[0]

            while not filename or filename in names_used:
                filename = f"{default_name:03}"
                default_name += 1

            names_used.add(filename)

            to_create.append(dict(im=im, filename=filename))
        except:
            raise HTTPException(400)

    chap_dir.mkdir()
    for pg in to_create:
        fp = chap_dir / f'{pg["filename"]}.png'
        pg["im"].save(fp)

    db = load_chapter_db(chap_dir)
    update_chapter(db, chapter)

    return get_chapter(cfg, series, chapter_filename)


class RenameChapterRequest(BaseModel):
    series: str
    chapter: str
    name: str


@router.patch("/chapter")
def rename_chapter(req: Request, body: RenameChapterRequest):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)

    cfg: Config = req.app.state.cfg

    try:
        db = load_chapter_db(
            cfg.root_image_folder / series / chapter,
            raise_on_missing=True,
        )
    except FileNotFoundError:
        raise HTTPException(400)

    update_chapter(db, body.name)
    return get_chapter(cfg, series, chapter)


class RenamePageRequest(BaseModel):
    series: str
    chapter: str
    pages: "list[RenamePageRequestItem]"


class RenamePageRequestItem(BaseModel):
    source: str
    destination: str


class DeleteChapterRequest(BaseModel):
    series: str
    chapter: str


@router.delete("/chapter")
def delete_chapter(req: Request, body: DeleteChapterRequest):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)

    cfg: Config = req.app.state.cfg

    fp = cfg.root_image_folder / series / chapter
    if not fp.exists():
        raise HTTPException(404)

    try:
        shutil.rmtree(fp)
    except:
        traceback.print_exc()
        raise HTTPException(500)

    return "ok"


@router.post("/page/{series}/{chapter}")
def add_page(req: Request, series: str, chapter: str, page: UploadFile):
    series = sanitize_or_raise_400(series)
    chapter = sanitize_or_raise_400(chapter)

    cfg: Config = req.app.state.cfg

    chap_dir = cfg.root_image_folder / series / chapter

    filename = (page.filename or "").split(".")[0]
    if filename:
        fp_page = chap_dir / f"{filename}.png"

        if fp_page.exists():
            raise HTTPException(400)
    else:
        current_pages = get_all_pages(cfg, series, chapter)

        fp_page = None
        while not fp_page or fp_page.exists():
            page_idx = len(current_pages) + 1
            fp_page = chap_dir / f"{page_idx:03}"

    try:
        im = Image.open(page.file)
        im.verify()
    except:
        raise HTTPException(400)

    try:
        im.save(fp_page)
    except FileNotFoundError:
        raise HTTPException(404)

    return get_all_pages(cfg, series, chapter)


@router.patch("/page")
def rename_page(
    req: Request,
    body: RenamePageRequest,
):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)

    cfg: Config = req.app.state.cfg

    targets = []
    all_sources = set()
    for pg in body.pages:
        source = sanitize_or_raise_400(pg.source)

        destination = pg.destination.split(".")[0] + ".png"
        destination = sanitize_or_raise_400(destination)

        fp_source = cfg.root_image_folder / series / chapter / source
        if not fp_source.exists():
            raise HTTPException(404)

        all_sources.add(fp_source)

        fp_dest = fp_source.parent / destination
        if fp_dest.exists() and fp_dest not in all_sources:
            raise HTTPException(400)

        targets.append(dict(fp_source=fp_source, fp_dest=fp_dest))

    for tgt in targets:
        try:
            im = Image.open(fp_source)
            im.verify()
        except:
            raise HTTPException(400)

        tgt["im"] = im

    for tgt in targets:
        tgt["fp_source"].unlink()

    for tgt in targets:
        im.save(tgt["fp_dest"])
        fp_source.unlink()

    return fp_dest.name


class DeletePageRequest(BaseModel):
    series: str
    chapter: str
    page: str


@router.delete("/page")
def delete_page(req: Request, body: DeletePageRequest):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)
    page = sanitize_or_raise_400(body.page)

    cfg: Config = req.app.state.cfg

    fp = cfg.root_image_folder / series / chapter / page
    if not fp.exists():
        raise HTTPException(404)

    fp.unlink()

    return "ok"


@router.get("/count/{series}")
def get_file_count_series(req: Request, series: str):
    series = sanitize_or_raise_400(series)

    cfg: Config = req.app.state.cfg

    fp = cfg.root_image_folder / series
    if not fp.exists():
        raise HTTPException(404)

    return count_file_types(fp)


@router.get("/count/{series}/{chapter}")
def get_file_count_chapter(req: Request, series: str, chapter: str):
    series = sanitize_or_raise_400(series)
    chapter = sanitize_or_raise_400(chapter)

    cfg: Config = req.app.state.cfg

    fp = cfg.root_image_folder / series / chapter
    if not fp.exists():
        raise HTTPException(404)

    return count_file_types(fp)
