from dataclasses import fields, is_dataclass
from pathlib import Path

import numpy as np
from fastapi import HTTPException
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
