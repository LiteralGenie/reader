import asyncio

from fastapi import APIRouter, Request
from fastapi_cache.decorator import cache

from ..db.llm_cache import load_llm_cache, select_best_defs, select_translation
from ..db.reader_db import load_reader_db
from ..llm.llm_worker import insert_llm_job

router = APIRouter()


@router.get("/mtl/{text}")
@cache()  # type: ignore
async def get_mtl(req: Request, text: str):
    if not req.app.state.cfg.use_llm_for_mtl:
        return None

    cache = load_llm_cache()

    translation = select_translation(cache, text)
    if translation is None:
        insert_llm_job(load_reader_db(), text, "mtl")

    while not translation:
        await asyncio.sleep(1)
        translation = select_translation(cache, text)

    return translation


@router.get("/best_defs/{text}")
@cache()  # type: ignore
async def get_best_defs(req: Request, text: str):
    if not req.app.state.cfg.use_llm_for_definition_sort:
        return None

    cache = load_llm_cache()

    best = select_best_defs(cache, text)
    if best is None:
        insert_llm_job(load_reader_db(), text, "best_defs")

    while not best:
        await asyncio.sleep(1)
        best = select_best_defs(cache, text)

    return best
