import io
import time
import traceback
from pathlib import Path
from typing import TypeAlias, cast

import requests
from bs4 import BeautifulSoup
from PIL import Image

from .config import Config
from .db.chapter_db import load_chapter_db, update_chapter
from .db.reader_db import ReaderDb, load_reader_db
from .job_utils import JobManager, start_job_worker

_JOB_TYPE = "import"

# time requested, bytes
RequestHistory: TypeAlias = list[tuple[float, int]]


def start_import_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        _JOB_TYPE,
        _process_all_jobs,
        initargs=(cfg,),
    )


def insert_import_job(
    db: ReaderDb,
    urls: list[str],
    chap_dir: Path,
    chap_name: str,
    min_width: int,
    min_height: int,
):
    print("Inserting import job for", urls)

    id = f"{urls}"

    jobber = JobManager(db, _JOB_TYPE)
    jobber.insert(
        id,
        dict(
            urls=urls,
            chap_dir=chap_dir,
            chap_name=chap_name,
            min_width=min_width,
            min_height=min_height,
        ),
    )
    db.commit()

    return id


def get_import_job_progress(db: ReaderDb, job_id: str):
    jobber = JobManager(db, _JOB_TYPE)
    progress = jobber.select_progress(job_id)
    return progress


def _process_all_jobs(cfg: Config, job_ids: list[str]):
    reader_db = load_reader_db()
    jobber = JobManager(reader_db, _JOB_TYPE)

    for id in job_ids:
        try:
            result = _process_job(
                cfg,
                jobber,
                id,
            )
        except:
            # Delete job on error
            traceback.print_exc()

            jobber.delete(id)
            reader_db.commit()

            raise

        jobber.set_result(id, result)
        jobber.db.commit()


def _process_job(
    cfg: Config,
    jobber: JobManager,
    job_id: str,
):
    job = jobber.select(job_id)
    print("Processing import job", job_id, job)

    if job["chap_dir"].exists():
        raise Exception()

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

    maybe_images: list[dict | str] = []

    # Extract all image urls from the original urls
    # (or the image itself if the url points directly to an image)
    for url in job["urls"]:
        try:
            # Fetch url
            _wait_rate_limit(history, cfg)
            resp = requests.get(url)
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
                    im=im,
                    size_bytes=len(resp.content),
                    src=url,
                )
            )
        else:
            # URL pointed to a doc with <img>s
            soup = BeautifulSoup(resp.text)
            imgs = soup.find_all("img")

            for el in imgs:
                src = el.get("src")
                if not src:
                    continue

                maybe_images.append(src)

    progress["phase"] = "downloading"
    progress["total"] = len(maybe_images)
    jobber.update_progress(job_id, progress)
    jobber.db.commit()

    rem_bytes = cfg.max_chapter_size_bytes
    idx_name = 1

    for image_or_url in maybe_images:
        # Check if we hit resource caps
        over_image_cap = len(progress["done"]) >= cfg.max_import_images_per_chapter
        over_size_cap = rem_bytes <= 0
        if over_image_cap or over_size_cap:
            url = image_or_url if isinstance(image_or_url, str) else image_or_url["src"]
            progress["ignored"].append(url)
            jobber.update_progress(job_id, progress)
            jobber.db.commit()
            continue

        # Download Image if we haven't already
        if isinstance(image_or_url, str):
            _wait_rate_limit(history, cfg)
            result = _download_image(image_or_url, rem_bytes)
            history.append((time.time(), result["size_bytes"]))

            if not result["success"]:
                progress["ignored"].append(image_or_url)
                jobber.update_progress(job_id, progress)
                jobber.db.commit()
                continue

            im: Image.Image = result["im"]
            url = image_or_url
            size_bytes = result["size_bytes"]
        else:
            im: Image.Image = image_or_url["im"]
            url = image_or_url["src"]
            size_bytes = image_or_url["size_bytes"]

        # Check dimensions
        matches_width = im.size[0] >= job["min_width"]
        matches_height = im.size[0] >= job["min_height"]
        if not matches_width or not matches_height:
            progress["ignored"].append(url)
            jobber.update_progress(job_id, progress)
            jobber.db.commit()
            continue

        # Save image
        fp_out = job["chap_dir"] / f"{idx_name:03}.png"
        im.save(fp_out)

        idx_name += 1
        rem_bytes -= size_bytes

        progress["done"].append(url)
        jobber.update_progress(job_id, progress)
        jobber.db.commit()

    db = load_chapter_db(job["chap_dir"])
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

    while (
        count >= cfg.max_import_requests_per_second
        or cfg.max_import_bytes_per_second >= size
    ):
        time.sleep(delay)

    return


def _download_image(url: str, max_size_bytes: int, chunk_size=8192) -> dict:
    print("downloading", url)

    try:
        buffer = bytearray()

        with requests.get(url, stream=True) as resp:
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
        )
    except:
        return dict(
            success=False,
            size_bytes=len(buffer),
        )
