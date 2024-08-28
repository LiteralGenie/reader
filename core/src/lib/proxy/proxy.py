import traceback

import requests

from ..config import Config
from ..db.reader_db import ReaderDb, load_reader_db
from ..job_utils import JobManager, start_job_worker
from .request_log import RequestLog

PROXY_JOB_TYPE = "proxy"


_REQ_LOG = RequestLog()


def start_proxy_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        PROXY_JOB_TYPE,
        _process_all_jobs,
        delay=0.1,
    )


def insert_proxy_job(db: ReaderDb, url: str, rate_limit: int):
    print("Inserting proxy job for", url)

    id = f"{url}"

    jobber = JobManager(db, PROXY_JOB_TYPE)
    jobber.insert(
        id,
        dict(
            url=url,
            rate_limit=rate_limit,
        ),
    )
    db.commit()

    return id


def _process_all_jobs(cfg: Config, job_ids: list[str]):
    reader_db = load_reader_db()
    jobber = JobManager(reader_db, PROXY_JOB_TYPE)

    for id in job_ids:
        try:
            result = _process_job(cfg, jobber, id)

            jobber.set_result(id, result)
            jobber.db.commit()
        except:
            traceback.print_exc()

            jobber.set_error(
                id,
                dict(error=traceback.format_exc()),
            )
            jobber.db.commit()


def _process_job(
    cfg: Config,
    jobber: JobManager,
    job_id: str,
):
    job = jobber.select(job_id)
    print("Processing proxy job", job_id, job)

    _REQ_LOG.wait_limit(job["url"], job["rate_limit"])

    resp = requests.get(job["url"])
    _REQ_LOG.add(job["url"])

    return dict(
        status_code=resp.status_code,
        text=resp.text,
    )
