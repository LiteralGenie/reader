import asyncio
import datetime
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Callable

from .config import Config
from .db.reader_db import ReaderDb, load_reader_db


@dataclass
class JobManager:
    db: ReaderDb
    job_type: str

    def select_all_pending(self) -> list[str]:
        rs = self.db.execute(
            """
            SELECT id 
            FROM jobs
            WHERE
                type = ?
                AND processing = 0
            """,
            [self.job_type],
        ).fetchall()

        return [r["id"] for r in rs]

    def lock_all(self, ids: list[str]):
        self.db.executemany(
            """
            UPDATE jobs 
            SET processing = 1
            WHERE 
                id = ?
                AND type = ?
            """,
            [(id, self.job_type) for id in ids],
        )

    def select(self, id: str) -> dict:
        r = self.db.execute(
            """
                SELECT data FROM jobs
                WHERE
                    id = ?
                    AND type = ?
                """,
            [id, self.job_type],
        ).fetchone()

        return json.loads(r["data"])

    def select_progress(self, id: str) -> dict | None:
        r = self.db.execute(
            """
                SELECT progress FROM jobs
                WHERE
                    id = ?
                    AND type = ?
                """,
            [id, self.job_type],
        ).fetchone()

        return json.loads(r["progress"]) if r else None

    def update_progress(self, id: str, progress: dict):
        self.db.execute(
            """
                UPDATE jobs 
                SET progress = ?
                WHERE 
                    id = ?
                    AND type = ?
                """,
            [json.dumps(progress), id, self.job_type],
        )

    def delete(self, id: str):
        self.db.execute(
            """
            DELETE FROM jobs
            WHERE
                id = ?
                AND type = ?
            """,
            [id, self.job_type],
        )

    def insert(self, id: str, data: dict):
        self.db.execute(
            """
            INSERT OR IGNORE INTO jobs (
                id, created_at, type, data, processing
            ) VALUES (
                ?, ?, ?, ?, ?
            )
            """,
            [
                id,
                datetime.datetime.now().isoformat(),
                self.job_type,
                json.dumps(data),
                False,
            ],
        )

    def set_result(self, id: str, result: dict):
        self.db.execute(
            """
            UPDATE jobs
            SET 
                result = ?,
                done_at = ?
            WHERE id = ?
            """,
            [
                json.dumps(result),
                datetime.datetime.now().isoformat(),
                id,
            ],
        )


def start_job_worker(
    cfg: Config,
    job_type: str,
    consume_fn: Callable[[Config, list[str]], None],
    initializer: Callable | None = None,
    initargs=(),
):
    exec = ProcessPoolExecutor(
        1,
        initializer=initializer,
        initargs=initargs,
    )

    async def fn():
        db = load_reader_db()
        jobber = JobManager(db, job_type)

        while True:
            todo = jobber.select_all_pending()

            if not todo:
                await asyncio.sleep(1)
                continue

            # Update processing status
            jobber.lock_all(todo)
            db.commit()

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(exec, consume_fn, cfg, todo)

    return asyncio.create_task(fn())


def start_job_purge_worker(
    age_seconds=600,
    check_freq_seconds=60,
):
    async def fn():
        db = load_reader_db()

        while True:
            cutoff = datetime.datetime.now() - datetime.timedelta(minutes=age_seconds)

            db.execute(
                """
                DELETE FROM jobs
                WHERE done_at < ?
                """,
                [cutoff],
            )
            db.commit()

            await asyncio.sleep(check_freq_seconds)

    return asyncio.create_task(fn())
