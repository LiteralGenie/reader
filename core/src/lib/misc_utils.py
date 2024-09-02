import json
from dataclasses import fields, is_dataclass
from pathlib import Path

import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from jamo import h2j, j2hcj
from pathvalidate import sanitize_filename


def dump_dataclass(instance, exclude: list[str] | None = None) -> dict:
    exclude = exclude or []

    data = dict()

    for f in fields(instance):
        if f.name in exclude:
            continue

        val = getattr(instance, f.name)

        if is_dataclass(val):
            data[f.name] = dump_dataclass(val, exclude)
        else:
            data[f.name] = _dump(val, exclude)

    return data


def _dump(x, exclude: list[str] | None):
    exclude = exclude or []

    if isinstance(x, (str, int, float, bool)):
        return x
    elif isinstance(x, (np.int64, np.int32, np.int16, np.int8)):  # type: ignore
        return int(x)
    elif isinstance(x, Path):
        return str(x)
    elif isinstance(x, list):
        return [_dump(v, exclude) for v in x]
    elif isinstance(x, tuple):
        return tuple(_dump(v, exclude) for v in x)
    elif isinstance(x, dict):
        return {k: _dump(v, exclude) for k, v in x.items() if k not in exclude}
    elif is_dataclass(x):
        return dump_dataclass(x, exclude)
    elif x is None:
        return None
    else:
        raise Exception()


def sanitize_or_raise_400(filename: str):
    result = sanitize_filename(filename).strip()
    if not result:
        raise HTTPException(400)

    return result


def download_stream(url: str, fp: Path, chunk_size=8192):
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(fp, "wb") as file:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                file.write(chunk)


def log_422s(app: FastAPI):
    from fastapi import Request, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):

        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        # or logger.error(f'{exc}')
        print(request, exc_str)
        content = {"status_code": 10422, "message": exc_str, "data": None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def dump_sse_event(data: dict) -> str:
    return "data: " + json.dumps(data) + "\n\n"


def to_jamo(text: str) -> list[str]:
    try:
        return [char for char in j2hcj(h2j(text))]
    except:
        # @todo: handle to_jamo() fail
        return [text]


def to_joined_jamo(text: str) -> str:
    return "".join(to_jamo(text))
