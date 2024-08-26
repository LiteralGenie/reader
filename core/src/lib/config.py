from dataclasses import dataclass
from pathlib import Path

import toml


@dataclass
class Config:
    root_image_folder: Path

    api_port: int

    det_weights: str
    reco_weights: str

    det_arch: str
    reco_arch: str

    det_input_size: int

    margin_size: int

    max_ocr_width: int

    use_gpu_for_ocr: bool

    use_llm_for_mtl: bool
    use_llm_for_definition_sort: bool

    llm_num_definitions: int

    llm_model_id: str
    llm_model_file: str

    llm_num_gpu_layers: int

    max_auto_cover_x: int
    max_auto_cover_y: int

    @classmethod
    def load(cls, data: dict) -> "Config":
        d = data.copy()

        for fp_key in [
            "root_image_folder",
        ]:
            d[fp_key] = Path(d[fp_key])

        return cls(**d)

    @classmethod
    def load_toml(cls, fp: Path) -> "Config":
        data = toml.loads(fp.read_text())
        return cls.load(data)
