import io
import re
import time
import traceback
from pathlib import Path
from typing import TypeAlias
from uuid import uuid4

import loguru
from bs4 import BeautifulSoup
from PIL import Image
from requests_cache import CachedSession, SQLiteCache
from yarl import URL

from .config import Config
from .db.chapter_db import load_chapter_db, update_chapter
from .db.reader_db import ReaderDb, load_reader_db
from .job_utils import JobManager, start_job_worker
from .paths import DATA_DIR, LOG_DIR

IMPORT_JOB_TYPE = "import"

_WORKER_SESSION: CachedSession = None  # type: ignore

# time requested, bytes
RequestHistory: TypeAlias = list[tuple[float, int]]

loguru.logger.add(
    LOG_DIR / "url_import.log",
    filter=lambda record: record["extra"].get("name") == "url_import",
    rotation="10 MB",
    retention=2,
)
_LOGGER = loguru.logger.bind(name="url_import")


def start_import_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        IMPORT_JOB_TYPE,
        _process_all_jobs,
        batch_size=1,
    )


def insert_import_job(
    db: ReaderDb,
    urls: list[str],
    chap_dir: Path,
    chap_name: str,
    min_width: int,
    min_height: int,
    patt: re.Pattern | None,
):
    id = uuid4().hex

    job = dict(
        urls=urls,
        chap_dir=str(chap_dir.absolute()),
        chap_name=chap_name,
        min_width=min_width,
        min_height=min_height,
        patt=patt.pattern if patt else None,
    )

    _LOGGER.info(f"Inserting import job {id} {job}")

    jobber = JobManager(db, IMPORT_JOB_TYPE)
    jobber.insert(id, job)
    db.commit()

    return id


def _process_all_jobs(cfg: Config, job_ids: list[str]):
    reader_db = load_reader_db()
    jobber = JobManager(reader_db, IMPORT_JOB_TYPE)

    global _WORKER_SESSION
    if _WORKER_SESSION is None:
        _WORKER_SESSION = CachedSession(
            backend=SQLiteCache(DATA_DIR / "http_cache.sqlite"),
            expire_after=10 * 86400,
        )

    for id in job_ids:
        try:
            _LOGGER.info(f"Processing import job {id}")
            result = _process_job(
                cfg,
                _WORKER_SESSION,
                jobber,
                id,
            )
            _LOGGER.info(
                f"Done with import job {id} with {len(result['done'])} downloaded and {len(result['ignored'])} ignored"
            )
        except:
            # Delete job on error
            traceback.print_exc()

            jobber.delete(id)
            reader_db.commit()

            _LOGGER.exception(f"Failed import job {id}")

        jobber.set_result(id, result)
        jobber.db.commit()


def _process_job(
    cfg: Config,
    session: CachedSession,
    jobber: JobManager,
    job_id: str,
):
    job = jobber.select(job_id)

    chap_dir = Path(job["chap_dir"])
    if chap_dir.exists():
        raise Exception()
    else:
        chap_dir.mkdir()

    url_patt = None
    if job["patt"]:
        url_patt = re.compile(job["patt"], flags=re.IGNORECASE)

    # Init progress
    progress: dict = dict(
        total=len(job["urls"]),
        done=[],
        ignored=[],
        phase="scanning",
    )
    jobber.update_progress(job_id, progress)
    jobber.db.commit()

    history: RequestHistory = []

    headers = {"User-Agent": cfg.user_agent_for_import}

    maybe_images: list[dict] = []

    # Extract all image urls from the original urls
    # (or the image itself if the url points directly to an image)
    for url in job["urls"]:
        try:
            origin = URL(url).origin()

            _wait_rate_limit(history, cfg)

            is_cached = session.cache.contains(url=url)
            resp = session.get(url, headers=headers)

            if not is_cached:
                history.append((time.time(), len(resp.content)))
        except:
            # traceback.print_exc()
            continue

        content_type = resp.headers.get("Content-Type") or ""
        if content_type.lower().startswith("image"):
            # URL pointed to an image
            try:
                im = Image.open(io.BytesIO(resp.content))
                im.copy().verify()
            except:
                continue

            maybe_images.append(
                dict(
                    type="image",
                    im=im,
                    size_bytes=len(resp.content),
                    src=url,
                )
            )
        else:
            # URL pointed to a doc with <img>s
            soup = BeautifulSoup(resp.text, "lxml")
            imgs = soup.find_all("img")

            for el in imgs:
                src = el.get("src")
                if not src:
                    continue

                if url_patt and not url_patt.search(src):
                    continue

                src_url = URL(src)
                if not src_url.is_absolute():
                    src_url = origin / src.strip("/")

                maybe_images.append(
                    dict(
                        type="url",
                        src=str(src_url),
                    )
                )

    # Truncate candidate list if way too many
    to_ignore = [
        x if isinstance(x, str) else x["src"]
        for x in maybe_images[cfg.max_import_candidates_per_chapter :]
    ]
    maybe_images = maybe_images[: cfg.max_import_candidates_per_chapter]

    progress["phase"] = "downloading"
    progress["total"] = len(maybe_images) + len(to_ignore)
    progress["ignored"] = to_ignore
    jobber.update_progress(job_id, progress)
    jobber.db.commit()

    rem_bytes = cfg.max_chapter_size_bytes
    idx_name = 1

    for image_or_url in maybe_images:
        # Check if we hit resource caps
        over_image_cap = len(progress["done"]) >= cfg.max_import_images_per_chapter
        over_size_cap = rem_bytes <= 0
        if over_image_cap or over_size_cap:
            url = image_or_url["src"]
            progress["ignored"].append(url)
            jobber.update_progress(job_id, progress)
            jobber.db.commit()
            continue

        # Download Image if we haven't already
        if image_or_url["type"] == "url":
            _wait_rate_limit(history, cfg)
            result = _download_image(
                session,
                image_or_url["src"],
                rem_bytes,
                headers,
            )

            if not result["is_cached"]:
                history.append((time.time(), result["size_bytes"]))

            if not result["success"]:
                progress["ignored"].append(image_or_url["src"])
                jobber.update_progress(job_id, progress)
                jobber.db.commit()
                continue

            im: Image.Image = result["im"]
            url = image_or_url["src"]
            size_bytes = result["size_bytes"]
        else:
            im: Image.Image = image_or_url["im"]
            url = image_or_url["src"]
            size_bytes = image_or_url["size_bytes"]

        # Check dimensions
        matches_width = im.size[0] >= job["min_width"]
        matches_height = im.size[1] >= job["min_height"]
        if not matches_width or not matches_height:
            progress["ignored"].append(url)
            jobber.update_progress(job_id, progress)
            jobber.db.commit()
            continue

        # Save image
        fp_out = chap_dir / f"{idx_name:03}.png"
        im.save(fp_out)

        idx_name += 1
        rem_bytes -= size_bytes

        progress["done"].append(url)
        jobber.update_progress(job_id, progress)
        jobber.db.commit()

    db = load_chapter_db(chap_dir)
    update_chapter(db, name=job["chap_name"])

    return progress


def _sum_history(history: RequestHistory, recency_seconds=1):
    count = 0
    size = 0
    cutoff = time.time() - recency_seconds

    for t, sz in reversed(history):
        if t < cutoff:
            break

        count += 1
        size += sz

    return count, size


def _wait_rate_limit(
    history: RequestHistory,
    cfg: Config,
    delay=0.1,
):
    count, size = _sum_history(history)

    while True:
        count, size = _sum_history(history)

        if (
            count < cfg.max_import_requests_per_second
            and size < cfg.max_import_bytes_per_second
        ):
            break

        time.sleep(delay)

    return


def _download_image(
    session: CachedSession,
    url: str,
    max_size_bytes: int,
    headers: dict[str, str],
    chunk_size=8192,
) -> dict:
    is_cached = session.cache.contains(url=url)

    print("downloading", url)

    try:
        buffer = bytearray()

        with session.get(url, headers=headers, stream=True) as resp:
            resp.raise_for_status()

            if int(resp.headers.get("Content-Length", "0")) > max_size_bytes:
                return dict(
                    success=False,
                    size_bytes=len(buffer),
                )

            for chunk in resp.iter_content(chunk_size=chunk_size):
                buffer += chunk

                if len(buffer) > max_size_bytes:
                    return dict(
                        success=False,
                        size_bytes=len(buffer),
                    )

        im = Image.open(io.BytesIO(buffer))
        im.copy().verify()

        return dict(
            im=im,
            success=True,
            size_bytes=len(buffer),
            is_cached=is_cached,
        )
    except:
        return dict(
            success=False,
            size_bytes=len(buffer),
            is_cached=is_cached,
        )
