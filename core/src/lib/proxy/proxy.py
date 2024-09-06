import base64
import traceback

import loguru
import requests

from ..config import Config
from ..db.reader_db import ReaderDb, load_reader_db
from ..job_utils import JobManager, start_job_worker
from ..paths import LOG_DIR
from .request_log import RequestLog

PROXY_JOB_TYPE = "proxy"

_REQ_LOG = RequestLog()

loguru.logger.add(
    LOG_DIR / "proxy.log",
    filter=lambda record: record["extra"].get("name") == "proxy",
    rotation="10 MB",
    retention=2,
)
_LOGGER = loguru.logger.bind(name="proxy")


def start_proxy_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        PROXY_JOB_TYPE,
        _process_all_jobs,
        delay=0.1,
    )


def insert_proxy_job(
    db: ReaderDb,
    url: str,
    rate_limit: int,
    user_agent: str | None = None,
):
    id = f"{url}"
    job = dict(
        url=url,
        rate_limit=rate_limit,
        user_agent=user_agent,
    )

    _LOGGER.info(f"Inserting proxy job {id} {job}")

    jobber = JobManager(db, PROXY_JOB_TYPE)
    jobber.insert(id, job)
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
    _LOGGER.info(f"Processing proxy job {job_id}")

    _REQ_LOG.wait_limit(job["url"], job["rate_limit"])

    headers = dict()
    if job["user_agent"]:
        headers["User-Agent"] = job["user_agent"]

    resp = requests.get(job["url"], headers=headers)
    _REQ_LOG.add(job["url"])

    return dict(
        status_code=resp.status_code,
        body=base64.b64encode(resp.content).decode("ascii"),
        headers=dict(resp.headers),
    )
