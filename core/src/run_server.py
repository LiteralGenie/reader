import argparse
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from lib.config import Config
from lib.handlers.series import get_all_series


@asynccontextmanager
async def _lifespan(app: FastAPI):
    args = _parse_args()
    app.state.args = args

    cfg = Config.load_toml(args.config_file)
    app.state.cfg = cfg

    yield


app = FastAPI(lifespan=_lifespan)


@app.get("/series")
def series():
    data = get_all_series(app.state.cfg)
    return data


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "config_file",
        type=Path,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable hot-reloading",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    cfg = Config.load_toml(args.config_file)

    uvicorn.run(
        "run_server:app",
        reload=args.debug,
        host="0.0.0.0",
        port=cfg.api.port,
    )
