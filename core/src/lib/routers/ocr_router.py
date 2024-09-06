import asyncio
import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..db.chapter_db import (delete_ocr_data, load_chapter_db, select_ocr_data,
                             update_ocr_text)
from ..db.reader_db import load_reader_db
from ..misc_utils import sanitize_or_raise_400
from ..ocr import get_all_ocr_data, insert_ocr_job
from . import EDIT_LOGGER

router = APIRouter()


@router.get("/ocr/{series}/{chapter}")
def ocr_for_chapter(req: Request, series: str, chapter: str):
    series = sanitize_or_raise_400(series)
    chapter = sanitize_or_raise_400(chapter)

    chap_dir: Path = req.app.state.cfg.root_image_folder / series / chapter
    if not chap_dir.exists():
        raise HTTPException(404)

    data = get_all_ocr_data(chap_dir)

    missing = [fp_image for fp_image in data if data[fp_image] is None]
    missing.sort()
    for fp_image in missing:
        insert_ocr_job(load_reader_db(), fp_image)

    resp = {fp_image.name: pg_data for fp_image, pg_data in data.items()}
    return resp


@router.get("/ocr/{series}/{chapter}/sse")
def poll_ocr(
    req: Request,
    series: str,
    chapter: str,
    pages: Annotated[list[str], Query()],
):
    series = sanitize_or_raise_400(series)
    chapter = sanitize_or_raise_400(chapter)

    chap_dir: Path = req.app.state.cfg.root_image_folder / series / chapter
    if not chap_dir.exists():
        raise HTTPException(404)

    if not pages:
        raise HTTPException(400)

    for filename in pages:
        if not (chap_dir / filename).exists():
            raise HTTPException(404)

    async def poll():
        db = load_chapter_db(chap_dir)

        pages_to_poll = pages.copy()
        pages_to_poll.sort()

        while pages_to_poll:
            fst = pages_to_poll[0]

            data = select_ocr_data(db, fst)
            if not data:
                await asyncio.sleep(1)
                continue

            resp = dict(filename=fst, data=data)
            resp = "data: " + json.dumps(resp) + "\n\n"
            yield resp

            pages_to_poll.pop(0)

        yield "data: close\n\n"

    return StreamingResponse(poll(), media_type="text/event-stream")


class UpdateBlockTextRequest(BaseModel):
    series: str
    chapter: str
    page: str
    block: str
    text: str


@router.patch("/ocr/text")
def update_block_text(req: Request, body: UpdateBlockTextRequest):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)

    if series != "tmp":
        raise HTTPException(
            400, "Edits to this demo chapter have been disabled"
        )

    chap_dir: Path = req.app.state.cfg.root_image_folder / series / chapter
    try:
        db = load_chapter_db(chap_dir, raise_on_missing=True)
    except FileNotFoundError:
        raise HTTPException(400)

    update_ocr_text(db, body.block, body.text)
    EDIT_LOGGER.info(f"Updated OCR block {body}")

    return "ok"


class DeleteBlockRequest(BaseModel):
    series: str
    chapter: str
    page: str
    block: str


@router.delete("/ocr/delete")
def delete_block(req: Request, body: DeleteBlockRequest):
    series = sanitize_or_raise_400(body.series)
    chapter = sanitize_or_raise_400(body.chapter)

    if series != "tmp":
        raise HTTPException(
            400, "Edits to this demo chapter have been disabled"
        )

    chap_dir: Path = req.app.state.cfg.root_image_folder / series / chapter
    try:
        db = load_chapter_db(chap_dir, raise_on_missing=True)
    except FileNotFoundError:
        raise HTTPException(400)

    delete_ocr_data(db, body.block)
    EDIT_LOGGER.info(f"Deleted OCR block {body}")

    return "ok"
