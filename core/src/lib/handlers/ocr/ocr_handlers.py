from pathlib import Path
from typing import Generator

import doctr
import torch
from comic_ocr.lib.constants import KOREAN_ALPHABET
from comic_ocr.lib.inference_utils import calc_windows, eval_window
from comic_ocr.lib.label_utils import OcrMatch
from doctr.models.predictor import OCRPredictor
from PIL import Image

from ...config import Config


def ocr_page(
    cfg: Config,
    predictor: OCRPredictor,
    fp_image: Path,
) -> Generator[float, None, list[OcrMatch]]:
    im = Image.open(fp_image)

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

    return matches


def load_predictor(cfg: Config) -> OCRPredictor:
    det_model = doctr.models.detection.__dict__[cfg.det_arch](
        pretrained=False,
        pretrained_backbone=False,
    )
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

    return predictor
