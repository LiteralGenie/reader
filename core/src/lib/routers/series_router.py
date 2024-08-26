from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pathvalidate import sanitize_filename
from PIL import Image
from pydantic import BaseModel

from ..db.series_db import load_series_db, update_series
from ..series import (
    create_series,
    get_all_chapters,
    get_all_pages,
    get_all_series,
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
    series = sanitize_filename(series)

    try:
        data = get_series(req.app.state.cfg, series)
        data["chapters"] = get_all_chapters(req.app.state.cfg, series)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@router.get("/series/{series}/{chapter}")
def chapter_by_id(req: Request, series: str, chapter: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)

    try:
        data = get_all_pages(req.app.state.cfg, series, chapter)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@router.get("/series/{series}/{chapter}/{page}")
def image_by_id(req: Request, series: str, chapter: str, page: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)
    page = sanitize_filename(page)

    fp: Path = req.app.state.cfg.series_folder / series / chapter / page
    if not fp.exists():
        raise HTTPException(404)

    return FileResponse(fp)


class CreateSeriesRequest(BaseModel):
    filename: str
    name: str


@router.post("/series")
def create_series_(req: Request, body: CreateSeriesRequest):
    filename = sanitize_filename(body.filename)

    try:
        create_series(req.app.state.cfg, filename, body.name)
    except FileExistsError:
        raise HTTPException(400)

    return get_series(req.app.state.cfg, filename)


@router.post("/series/{series}/cover")
def upsert_series_cover(req: Request, series: str, cover: UploadFile):
    series = sanitize_filename(series)

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


class UpdateSeriesRequest(BaseModel):
    filename: str
    name: str | None
    id_mangaupdates: str | None
    id_mangadex: str | None


@router.post("/series/{series}")
def update_series_(req: Request, body: UpdateSeriesRequest):
    filename = sanitize_filename(body.filename)

    try:
        series_dir = req.app.state.cfg.series_folder / filename
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
