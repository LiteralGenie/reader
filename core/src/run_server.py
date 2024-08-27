import argparse
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from lib.config import Config
from lib.db.reader_db import clear_jobs, load_reader_db
from lib.job_utils import start_job_purge_worker
from lib.llm.llm_worker import start_llm_job_worker
from lib.nlp import start_nlp_pool
from lib.ocr import start_ocr_job_worker
from lib.routers import dictionary_router, llm_router, ocr_router, series_router

# web gui doesn't support custom config so just hard code the config here too
CONFIG_FILE = Path(__file__).parent.parent.parent / "config.toml"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Cache
    FastAPICache.init(InMemoryBackend(), expire=86400)

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
    start_job_purge_worker()

    start_ocr_job_worker(cfg)
    start_llm_job_worker(cfg)

    yield


app = FastAPI(lifespan=_lifespan)

app.include_router(series_router.router)
app.include_router(dictionary_router.router)
app.include_router(ocr_router.router)
app.include_router(llm_router.router)


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
