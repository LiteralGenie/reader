import argparse
import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from konlpy.tag import Kkma
from lib.chapter_db import get_ocr_data, load_chapter_db
from lib.config import Config
from lib.nlp import get_pos_by_word, get_wikti_defs
from lib.ocr import get_all_ocr_data, insert_page_job, start_page_job_worker
from lib.reader_db import clear_jobs, load_reader_db
from lib.series import get_all_chapters, get_all_pages, get_all_series
from pathvalidate import sanitize_filename

# web gui doesn't support custom config so just hard code the config here too
CONFIG_FILE = Path(__file__).parent.parent.parent / "config.toml"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Load globals
    args = _parse_args()
    app.state.args = args

    # cfg = Config.load_toml(args.config_file)
    cfg = Config.load_toml(CONFIG_FILE)
    app.state.cfg = cfg

    app.state.kkma = Kkma()
    app.state.kkma.pos("안녕, 세상")  # warm up whatever caches

    # Start job workers
    reader_db = load_reader_db()
    clear_jobs(reader_db)
    start_page_job_worker(cfg, reader_db)

    yield


app = FastAPI(lifespan=_lifespan)


@app.get("/series")
def series():
    data = get_all_series(app.state.cfg)
    return data


@app.get("/series/{series}")
def series_by_id(series: str):
    series = sanitize_filename(series)

    try:
        data = get_all_chapters(app.state.cfg, series)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@app.get("/series/{series}/{chapter}")
def chapter_by_id(series: str, chapter: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)

    try:
        data = get_all_pages(app.state.cfg, series, chapter)
    except FileNotFoundError:
        raise HTTPException(404)

    return data


@app.get("/series/{series}/{chapter}/{page}")
def image_by_id(series: str, chapter: str, page: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)
    page = sanitize_filename(page)

    fp: Path = app.state.cfg.series_folder / series / chapter / page
    if not fp.exists():
        raise HTTPException(404)

    return FileResponse(fp)


@app.get("/ocr/{series}/{chapter}")
def ocr_for_chapter(series: str, chapter: str):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)

    chap_dir: Path = app.state.cfg.series_folder / series / chapter
    if not chap_dir.exists():
        raise HTTPException(404)

    data = get_all_ocr_data(chap_dir)

    missing = [fp_image for fp_image in data if data[fp_image] is None]
    missing.sort()
    for fp_image in missing:
        insert_page_job(load_reader_db(), fp_image)

    return {fp_image.name: pg_data for fp_image, pg_data in data.items()}


@app.get("/ocr/{series}/{chapter}/sse")
def poll_ocr(
    series: str,
    chapter: str,
    pages: Annotated[list[str], Query()],
):
    series = sanitize_filename(series)
    chapter = sanitize_filename(chapter)

    chap_dir: Path = app.state.cfg.series_folder / series / chapter
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

            data = get_ocr_data(db, fst)
            if not data:
                await asyncio.sleep(1)
                continue

            resp = dict(filename=fst, data=data)
            resp = "data: " + json.dumps(resp) + "\n\n"
            yield resp

            pages_to_poll.pop(0)

        yield "data: close\n\n"

    return StreamingResponse(poll(), media_type="text/event-stream")


@app.get("/nlp/{text}")
def nlp(text: str):
    words = get_pos_by_word(app.state.kkma, text)

    for grp in words:
        for info in grp:
            info["defs"] = get_wikti_defs(info["text"], info["pos"])

    return dict(pos=words)


def _parse_args():
    parser = argparse.ArgumentParser()

    # parser.add_argument(
    #     "config_file",
    #     type=Path,
    # )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable hot-reloading",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    # cfg = Config.load_toml(args.config_file)
    cfg = Config.load_toml(CONFIG_FILE)

    uvicorn.run(
        "run_server:app",
        reload=args.debug,
        host="0.0.0.0",
        port=cfg.api_port,
    )
