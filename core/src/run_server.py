import argparse
import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from lib.config import Config
from lib.db.chapter_db import get_ocr_data, load_chapter_db
from lib.db.dictionary_db import count_examples, load_dictionary_db, select_examples
from lib.db.mtl_cache import load_mtl_cache, select_translation
from lib.db.reader_db import clear_jobs, load_reader_db
from lib.mtl import insert_mtl_job, parse_mtl, start_mtl_job_worker
from lib.nlp import get_defs, get_pos_by_word, get_pos_by_word_dumb, start_nlp_pool
from lib.ocr import get_all_ocr_data, insert_ocr_job, start_ocr_job_worker
from lib.series import get_all_chapters, get_all_pages, get_all_series
from pathvalidate import sanitize_filename

# web gui doesn't support custom config so just hard code the config here too
CONFIG_FILE = Path(__file__).parent.parent.parent / "config.toml"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Global args
    args = _parse_args()
    app.state.args = args

    # Global cfg
    # cfg = Config.load_toml(args.config_file)
    cfg = Config.load_toml(CONFIG_FILE)
    app.state.cfg = cfg

    # Global nlp thing
    app.state.kkma_pool = start_nlp_pool()

    # Start job workers
    clear_jobs(load_reader_db())
    start_ocr_job_worker(cfg)
    start_mtl_job_worker(cfg)

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
        insert_ocr_job(load_reader_db(), fp_image)

    resp = {fp_image.name: pg_data for fp_image, pg_data in data.items()}
    if not missing:
        return JSONResponse(
            resp,
            headers={
                "Cache-Control": f"max-age={365*86400}",
            },
        )
    else:
        return JSONResponse(
            resp,
            headers={
                "Cache-Control": f"no-cache",
            },
        )


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
    words = get_pos_by_word(app.state.kkma_pool, text)
    if not words:
        words = get_pos_by_word_dumb(app.state.kkma_pool, text)

    for grp in words:
        for info in grp:
            info["defs"] = get_defs(info["text"], info["pos"])

    return JSONResponse(
        words,
        headers={
            "Cache-Control": f"max-age={365*86400}",
        },
    )


@app.get("/examples/{text}")
def examples(
    text: str,
    offset: Annotated[str, Query()] = "0",
    limit: Annotated[str, Query()] = "10",
):
    db = load_dictionary_db()

    num_offset = int(offset)
    num_limit = min(int(limit), 1000)

    return select_examples(db, text, num_offset, num_limit)


@app.get("/examples/{text}/count")
def examples_count(text: str):
    db = load_dictionary_db()

    return count_examples(db, text)


@app.get("/mtl/{text}")
async def get_mtl(text: str):
    if not app.state.cfg.use_llm:
        return None

    cache = load_mtl_cache()

    translation = select_translation(cache, text)
    if translation is None:
        insert_mtl_job(load_reader_db(), text)

    while not translation:
        await asyncio.sleep(1)
        translation = select_translation(cache, text)

    parsed = parse_mtl(translation)
    return parsed


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
