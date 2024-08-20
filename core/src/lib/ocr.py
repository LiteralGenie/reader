import asyncio
import json
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Generator

import doctr
import torch
from comic_ocr.lib.constants import KOREAN_ALPHABET
from comic_ocr.lib.inference_utils import calc_windows, eval_window
from comic_ocr.lib.label_utils import OcrMatch
from doctr.models.predictor import OCRPredictor
from PIL import Image

from .chapter_db import get_ocr_data, load_chapter_db
from .config import Config
from .misc_utils import dump_dataclass
from .reader_db import ReaderDb, load_reader_db

_JOB_TYPE = "page"


def get_all_ocr_data(chap_dir: Path) -> dict[Path, dict | None]:
    fp_images = [
        *chap_dir.glob("*.jpg"),
        *chap_dir.glob("*.png"),
    ]

    db = load_chapter_db(chap_dir)

    data: dict[Path, dict | None] = dict()
    for fp in fp_images:
        data[fp] = get_ocr_data(db, fp.name)

    return data


def start_page_job_worker(cfg: Config, reader_db: ReaderDb):
    exec = ProcessPoolExecutor(1)

    async def fn():
        while True:
            todo = reader_db.execute(
                """
                    SELECT id 
                    FROM jobs
                    WHERE
                        type = ?
                        AND processing = 0
                    """,
                [_JOB_TYPE],
            ).fetchall()

            if not todo:
                await asyncio.sleep(1)
                continue

            # Update processing status
            reader_db.executemany(
                """
                UPDATE jobs 
                SET processing = 1
                WHERE 
                    id = ?
                    AND type = ?
                """,
                [(r["id"], _JOB_TYPE) for r in todo],
            )
            reader_db.commit()

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                exec,
                process_all_page_jobs,
                cfg,
                [r["id"] for r in todo],
            )

    return asyncio.create_task(fn())


def insert_page_job(db: ReaderDb, fp_image: Path):
    print("Inserting page job for", fp_image)
    data = dict(
        fp_image=str(fp_image),
        chap_dir=str(fp_image.parent),
    )

    db.execute(
        """
        INSERT OR IGNORE INTO jobs (
            id, type, data, processing, progress
        ) VALUES (
            ?, ?, ?, ?, ?
        )
        """,
        [str(fp_image), _JOB_TYPE, json.dumps(data), False, 0],
    )
    db.commit()


def process_all_page_jobs(cfg: Config, job_ids: list[str]):
    predictor = _load_predictor(cfg)

    for id in job_ids:
        _process_page_job(cfg, predictor, id)


def _process_page_job(
    cfg: Config,
    predictor: OCRPredictor,
    job_id: str,
):
    predictor = _load_predictor(cfg)

    reader_db = load_reader_db()

    try:
        # Get job data
        job = reader_db.execute(
            """
            SELECT data FROM jobs
            WHERE
                id = ?
                AND type = ?
            """,
            [job_id, _JOB_TYPE],
        ).fetchone()

        print("Processing page job", job_id, job["data"])

        job = json.loads(job["data"])

        # Generate OCR data
        fp_image = Path(job["fp_image"])

        ocr_iter = _ocr_page(
            cfg,
            predictor,
            fp_image,
        )

        try:
            while True:
                progress = next(ocr_iter)

                reader_db.execute(
                    """
                        UPDATE jobs 
                        SET progress = ?
                        WHERE 
                            id = ?
                            AND type = ?
                        """,
                    [progress, job_id, _JOB_TYPE],
                )
                reader_db.commit()

                print(f"OCR job {job_id} at {progress:.0%}")
        except StopIteration as e:
            matches = e.value

        # Insert OCR data
        data = [dump_dataclass(m) for m in matches]

        chap_db = load_chapter_db(Path(job["chap_dir"]))
        chap_db.execute(
            """
            INSERT INTO ocr_data (
                filename, data
            ) VALUES (
                ?, ?
            )
            """,
            [fp_image.name, json.dumps(data)],
        )
        chap_db.commit()
    except:
        # Delete job on error
        traceback.print_exc()

        reader_db.execute(
            """
            DELETE FROM jobs
            WHERE
                id = ?
                AND type = ?
            """,
            [job_id, _JOB_TYPE],
        )
        reader_db.commit()

        raise


def _ocr_page(
    cfg: Config,
    predictor: OCRPredictor,
    fp_image: Path,
) -> Generator[float, None, list[OcrMatch]]:
    im = Image.open(fp_image)

    resize_mult = 1
    if im.size[0] > cfg.max_ocr_width:
        w, h = im.size

        resize_mult = cfg.max_ocr_width / w
        new_size = (int(w * resize_mult), int(h * resize_mult))

        print(f"Resizing image from {(w,h)} to {new_size}")
        im = im.resize(new_size)

    windows = calc_windows(
        im.size,
        cfg.det_input_size,
        cfg.margin_size,
    )

    yield 0

    matches: list[OcrMatch] = []
    for idx, w in enumerate(windows):
        r = eval_window(predictor, im, w, 0)

        matches.extend(r["matches"])

        percent_done = (idx + 1) / len(windows)
        yield percent_done

    if resize_mult != 1:
        matches = [_rescale(m, 1 / resize_mult) for m in matches]

    return matches


def _load_predictor(cfg: Config) -> OCRPredictor:
    det_model = doctr.models.detection.__dict__[cfg.det_arch](
        pretrained=False,
        pretrained_backbone=False,
    )
    if cfg.det_weights:
        print(f"Loading detector model weights from {cfg.det_weights}")
        det_params = torch.load(
            Path(cfg.det_weights),
            map_location="cpu",
            weights_only=True,
        )
        det_model.load_state_dict(det_params)

    reco_model = doctr.models.recognition.__dict__[cfg.reco_arch](
        vocab=KOREAN_ALPHABET,
        pretrained=False,
        pretrained_backbone=False,
    )
    if cfg.reco_weights:
        print(f"Loading recognizer model weights from {cfg.reco_weights}")
        reco_params = torch.load(
            Path(cfg.reco_weights),
            map_location="cpu",
            weights_only=True,
        )
        reco_model.load_state_dict(reco_params)

    predictor = doctr.models.ocr_predictor(
        det_arch=det_model,
        reco_arch=reco_model,
    )

    if cfg.use_gpu:
        predictor = predictor.cuda()
        print("Running OCR models on GPU")
    else:
        print("Running OCR models on CPU")

    return predictor


def _rescale(match: OcrMatch, k: float) -> OcrMatch:
    y1, x1, y2, x2 = match.bbox
    y1 = int(y1 * k)
    x1 = int(x1 * k)
    y2 = int(y2 * k)
    x2 = int(x2 * k)

    bbox = (y1, x1, y2, x2)

    return OcrMatch(
        bbox,
        match.confidence,
        match.value,
    )
