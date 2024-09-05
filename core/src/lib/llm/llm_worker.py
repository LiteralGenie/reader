import gc
import json
import traceback
from typing import Literal

import torch
from llama_cpp import Llama

from ..config import Config
from ..db.llm_cache import insert_best_defs, insert_translation, load_llm_cache
from ..db.reader_db import ReaderDb, load_reader_db
from ..job_utils import JobManager, start_job_worker
from .best_defs import get_best_defs
from .mtl import mtl

_JOB_TYPE = "llm"


_WORKER_LLM: Llama | None = None


def start_llm_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        _JOB_TYPE,
        _process_all_jobs,
        idle_fn=_unload_worker,
        idle_time=30,
    )


def insert_llm_job(
    db: ReaderDb,
    text: str,
    type: Literal["mtl", "best_defs"],
):
    text = text.strip()

    print("Inserting llm job for", type, text)

    id = f"{type}_{text}"

    jobber = JobManager(db, _JOB_TYPE)
    jobber.insert(
        id,
        dict(
            text=text,
            type=type,
        ),
    )
    db.commit()


def _process_all_jobs(cfg: Config, job_ids: list[str]):
    reader_db = load_reader_db()
    jobber = JobManager(reader_db, _JOB_TYPE)

    global _WORKER_LLM
    if _WORKER_LLM is None:
        _WORKER_LLM = _init_worker(cfg)

    for id in job_ids:
        try:
            _process_job(
                cfg,
                jobber,
                _WORKER_LLM,
                id,
            )
        except:
            # Delete job on error
            traceback.print_exc()

            jobber.delete(id)
            reader_db.commit()

            raise


def _process_job(
    cfg: Config,
    jobber: JobManager,
    llm: Llama,
    job_id: str,
):
    # Get job data
    job = jobber.select(job_id)
    print("Processing llm job", job_id, job["text"])

    cache = load_llm_cache()

    if job["type"] == "mtl":
        translation = mtl(llm, job["text"])
        insert_translation(cache, job["text"], json.dumps(translation))
    else:
        best_defs = get_best_defs(llm, job["text"], cfg.llm_num_definitions)
        insert_best_defs(cache, job["text"], best_defs)

    cache.commit()


def _init_worker(cfg: Config):
    return Llama.from_pretrained(
        cfg.llm_model_id,
        cfg.llm_model_file,
        n_ctx=2048,
        n_gpu_layers=cfg.llm_num_gpu_layers,
    )


def _unload_worker():
    global _WORKER_LLM
    if not _WORKER_LLM:
        return

    print("unloading llm")

    _WORKER_LLM = None

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
