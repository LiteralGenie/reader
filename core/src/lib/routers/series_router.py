from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi_cache.decorator import cache
from pathvalidate import sanitize_filename

from ..series import get_all_chapters, get_all_pages, get_all_series

router = APIRouter()


@router.get("/series")
def seriesr(request: Request):
    data = get_all_series(request.app.state.cfg)
    return data


@router.get("/series/{series}")
def series_by_id(request: Request, series: str):
    series = sanitize_filename(series)

    try:
        data = get_all_chapters(request.app.state.cfg, series)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@router.get("/series/{series}/{chapter}")
def chapter_by_id(request: Request, series: str, chapter: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)

    try:
        data = get_all_pages(request.app.state.cfg, series, chapter)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@router.get("/series/{series}/{chapter}/{page}")
def image_by_id(request: Request, series: str, chapter: str, page: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)
    page = sanitize_filename(page)

    fp: Path = request.app.state.cfg.series_folder / series / chapter / page
    if not fp.exists():
        raise HTTPException(404)

    return FileResponse(fp)
