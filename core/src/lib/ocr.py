import json
import traceback
from itertools import chain
from pathlib import Path
from typing import Generator
from uuid import uuid4

import doctr
import torch
from comic_ocr.lib.constants import KOREAN_ALPHABET
from comic_ocr.lib.inference_utils import calc_windows, eval_window
from comic_ocr.lib.label_utils import OcrMatch, stitch_blocks, stitch_lines
from doctr.models.predictor import OCRPredictor
from PIL import Image

from .config import Config
from .constants import SUPPORTED_IMAGE_EXTENSIONS
from .db.chapter_db import insert_ocr_data, load_chapter_db, select_ocr_data
from .db.reader_db import ReaderDb, load_reader_db
from .job_utils import JobManager, start_job_worker

_JOB_TYPE = "ocr"


def get_all_ocr_data(chap_dir: Path) -> dict[Path, dict | None]:
    globs = [chap_dir.glob(f"*{ext}") for ext in SUPPORTED_IMAGE_EXTENSIONS]
    fp_images = list(chain(*globs))

    db = load_chapter_db(chap_dir)

    data: dict[Path, dict | None] = dict()
    for fp in fp_images:
        data[fp] = select_ocr_data(db, fp.name)

    return data


def start_ocr_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        _JOB_TYPE,
        _process_all_jobs,
        initializer=_init_worker,
        initargs=(cfg,),
    )


def insert_ocr_job(db: ReaderDb, fp_image: Path):
    print("Inserting ocr job for", fp_image)

    jobber = JobManager(db, _JOB_TYPE)
    jobber.insert(
        str(fp_image),
        dict(
            fp_image=str(fp_image),
            chap_dir=str(fp_image.parent),
        ),
    )
    db.commit()


def _process_all_jobs(cfg: Config, job_ids: list[str]):
    reader_db = load_reader_db()
    jobber = JobManager(reader_db, _JOB_TYPE)

    for id in job_ids:
        try:
            _process_job(
                cfg,
                _WORKER_PREDICTOR,
                jobber,
                id,
            )
        except:
            # Delete job on error
            traceback.print_exc()

            jobber.delete(id)
            reader_db.commit()


_WORKER_PREDICTOR: OCRPredictor = None  # type: ignore


def _init_worker(cfg: Config):
    global _WORKER_PREDICTOR
    _WORKER_PREDICTOR = _load_predictor(cfg)


def _process_job(
    cfg: Config,
    predictor: OCRPredictor,
    jobber: JobManager,
    job_id: str,
):
    # Get job data
    job = jobber.select(job_id)
    print("Processing ocr job", job_id, job)

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

            jobber.update_progress(job_id, progress)
            jobber.db.commit()

            print(f"OCR job {job_id} at {progress:.0%}")
    except StopIteration as e:
        matches = e.value

    # Group words into blocks (speech bubbles)
    lines = stitch_lines(matches)
    blocks = stitch_blocks(lines)

    # Insert OCR data
    chap_db = load_chapter_db(Path(job["chap_dir"]))

    for blk in blocks:
        insert_ocr_data(chap_db, fp_image.name, blk)

    chap_db.execute(
        """
        UPDATE pages
        SET done_ocr = 1
        WHERE filename = ?
        """,
        [fp_image.name],
    )

    chap_db.commit()


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

    if cfg.use_gpu_for_ocr:
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
