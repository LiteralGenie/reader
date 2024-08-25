from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi_cache.decorator import cache

from ..db.dictionary_db import (
    count_definitions,
    count_examples,
    load_dictionary_db,
    select_definitions,
    select_examples,
)
from ..nlp import get_defs, get_pos_by_word, get_pos_by_word_dumb

router = APIRouter()


@router.get("/nlp/{text}")
@cache(expire=365 * 86400)  # type: ignore
def nlp(req: Request, text: str):
    words = get_pos_by_word(req.app.state.kkma_pool, text)
    if not words:
        words = get_pos_by_word_dumb(req.app.state.kkma_pool, text)

    for w in words:
        for part in w:
            part["defs"] = get_defs(part["text"], part["pos"])

    return words


@router.get("/examples/{text}")
def examples(
    text: str,
    offset: Annotated[str, Query()] = "0",
    limit: Annotated[str, Query()] = "10",
):
    db = load_dictionary_db()

    num_offset = int(offset)
    num_limit = min(int(limit), 1000)

    return select_examples(db, text, num_offset, num_limit)


@router.get("/examples/{text}/count")
@cache()  # type: ignore
def examples_count(text: str):
    db = load_dictionary_db()
    return count_examples(db, text)


@router.get("/definitions/{text}")
def definitions(
    text: str,
    offset: Annotated[str, Query()] = "0",
    limit: Annotated[str, Query()] = "10",
):
    db = load_dictionary_db()

    num_offset = int(offset)
    num_limit = min(int(limit), 1000)

    return select_definitions(db, text, num_offset, num_limit)


@router.get("/definitions/{text}/count")
@cache()  # type: ignore
def definitions_count(text: str):
    db = load_dictionary_db()
    return count_definitions(db, text)
