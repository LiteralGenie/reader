import base64
import shutil
import time
import traceback
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from pydantic import BaseModel

from ..config import Config
from ..db.chapter_db import load_chapter_db, update_chapter
from ..db.reader_db import load_reader_db
from ..db.series_db import load_series_db, update_series
from ..job_utils import JobManager, wait_job
from ..misc_utils import sanitize_or_raise_400
from ..proxy.proxy import PROXY_JOB_TYPE, insert_proxy_job
from ..series import (
    count_file_types,
    create_series,
    get_all_chapters,
    get_all_pages,
    get_all_series,
    get_chapter,
    get_series,
    raise_on_size_limit,
    upsert_cover,
    validate_image_upload,
)
from ..url_import import get_import_job_progress, insert_import_job

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


@router.post("/series")
def create_series_(
    req: Request,
    filename: str = Form(),
    name: str = Form(),
    cover: UploadFile | None = File(None),
):
    filename = sanitize_or_raise_400(filename)

    cfg: Config = req.app.state.cfg

    cover_im = None
    if cover:
        cover_im = validate_image_upload(cover, cfg.max_cover_image_size_bytes)

    try:
        create_series(cfg, filename, name)
    except FileExistsError:
        raise HTTPException(400)

    if cover_im:
        upsert_cover(cfg, filename, cover_im)

    return get_series(cfg, filename)


@router.get("/cover/{series}/{filename}")
def get_series_cover(req: Request, series: str, filename: str):
    series = sanitize_or_raise_400(series)
    filename = sanitize_or_raise_400(filename)

    cfg: Config = req.app.state.cfg

    fp = cfg.root_image_folder / series / filename
    if not fp.exists():
        return HTTPException(404)

    return FileResponse(fp)


@router.patch("/cover/{series}/auto")
def upsert_series_cover_auto(req: Request, series: str):
    series = sanitize_or_raise_400(series)

    cfg: Config = req.app.state.cfg

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


@router.patch("/series")
def update_series_(
    req: Request,
    filename: str = Form(),
    name: str | None = Form(None),
    id_mangaupdates: str | None = Form(None),
    id_mangadex: str | None = Form(None),
    cover: UploadFile | None = Form(None),
):
    filename = sanitize_or_raise_400(filename)

    cfg: Config = req.app.state.cfg

    try:
        series_dir = cfg.root_image_folder / filename
        db = load_series_db(series_dir, raise_on_missing=True)
    except FileNotFoundError:
        raise HTTPException(404)

    if cover:
        cover_im = validate_image_upload(cover, cfg.max_cover_image_size_bytes)
        upsert_cover(cfg, filename, cover_im)

    update_series(
        db,
        name,
        id_mangaupdates,
        id_mangadex,
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

    raise_on_size_limit(pages, cfg.max_chapter_size_bytes)

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
            im.copy().verify()

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

    size = page.size
    if not size:
        raise HTTPException(411)

    current_pages = get_all_pages(cfg, series, chapter)
    rem_size = cfg.max_chapter_size_bytes - sum(pg["size"] for pg in current_pages)
    if size > rem_size:
        raise HTTPException(413)

    chap_dir = cfg.root_image_folder / series / chapter

    filename = (page.filename or "").split(".")[0]
    if filename:
        fp_page = chap_dir / f"{filename}.png"

        if fp_page.exists():
            raise HTTPException(400)
    else:
        fp_page = None
        while not fp_page or fp_page.exists():
            page_idx = len(current_pages) + 1
            fp_page = chap_dir / f"{page_idx:03}"

    try:
        im = Image.open(page.file)
        im.copy().verify()
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
            im.copy().verify()
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


class ImportChapterRequest(BaseModel):
    series: str
    chapter: str
    chapter_name: str
    urls: list[str]


@router.post("/import_chapter")
def import_chapter(req: Request, body: ImportChapterRequest):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)

    cfg: Config = req.app.state.cfg

    chap_dir = cfg.root_image_folder / series / chapter
    if chap_dir.exists():
        raise HTTPException(400)

    db = load_reader_db()
    job_id = insert_import_job(
        db,
        body.urls,
        chap_dir,
        body.chapter_name,
    )

    return job_id, chapter


@router.get("/import_chapter/{job_id}")
def import_chapter_progress(req: Request, job_id: str):
    db = load_reader_db()

    progress = get_import_job_progress(db, job_id)
    return progress


@router.get("/proxy/mangadex/{rest:path}")
def proxy_mangadex_api(req: Request, rest: str):
    db = load_reader_db()
    cfg: Config = req.app.state.cfg

    url = f"https://api.mangadex.org/{rest}"
    job_id = insert_proxy_job(
        db,
        url,
        cfg.max_mangadex_requests_per_second,
        user_agent="https://github.com/LiteralGenie/reader",
    )
    result, error = wait_job(
        JobManager(db, PROXY_JOB_TYPE),
        job_id,
        delay=0.1,
    )

    if result and result["status_code"] == 200:
        return Response(
            status_code=result["status_code"],
            content=base64.b64decode(result["body"]),
            # headers=result["headers"],
        )
    elif result:
        raise HTTPException(result["status_code"], result)
    else:
        raise HTTPException(500)


@router.get("/proxy/mangadex_cover/{manga_id}/{cover_filename}")
def proxy_mangadex_cover(req: Request, manga_id: str, cover_filename: str):
    db = load_reader_db()
    cfg: Config = req.app.state.cfg

    url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_filename}"
    job_id = insert_proxy_job(
        db,
        url,
        cfg.max_mangadex_requests_per_second,
        user_agent="https://github.com/LiteralGenie/reader",
    )
    result, error = wait_job(
        JobManager(db, PROXY_JOB_TYPE),
        job_id,
        delay=0.1,
    )

    if result and result["status_code"] == 200:
        return Response(
            status_code=result["status_code"],
            content=base64.b64decode(result["body"]),
            headers=result["headers"],
        )
    elif result:
        raise HTTPException(result["status_code"], result)
    else:
        raise HTTPException(500)


@router.get("/proxy/mangaupdates/{rest:path}")
def proxy_mangaupdates_api(req: Request, rest: str):
    db = load_reader_db()
    cfg: Config = req.app.state.cfg

    url = f"https://api.mangaupdates.com/v1/{rest}"
    job_id = insert_proxy_job(
        db,
        url,
        cfg.max_bakaupdate_requests_per_second,
    )
    result, error = wait_job(
        JobManager(db, PROXY_JOB_TYPE),
        job_id,
        delay=0.1,
    )

    if result and result["status_code"] == 200:
        return Response(
            status_code=result["status_code"],
            content=base64.b64decode(result["body"]),
            # headers=result["headers"],
        )
    elif result:
        raise HTTPException(result["status_code"], result)
    else:
        raise HTTPException(500)


@router.get("/proxy/mangaupdates_cover/{rest:path}")
def proxy_mangaupdates_cover(req: Request, rest: str):
    db = load_reader_db()
    cfg: Config = req.app.state.cfg

    url = f"https://cdn.mangaupdates.com/{rest}"
    job_id = insert_proxy_job(
        db,
        url,
        cfg.max_bakaupdate_requests_per_second,
    )
    result, error = wait_job(
        JobManager(db, PROXY_JOB_TYPE),
        job_id,
        delay=0.1,
    )

    if result and result["status_code"] == 200:
        return Response(
            status_code=result["status_code"],
            content=base64.b64decode(result["body"]),
            headers=result["headers"],
        )
    elif result:
        raise HTTPException(result["status_code"], result)
    else:
        raise HTTPException(500)
