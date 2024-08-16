from dataclasses import dataclass
from pathlib import Path

import toml


@dataclass
class Config:
    series_folder: Path

    @classmethod
    def load(cls, data: dict) -> "Config":
        d = data.copy()

        for fp_key in [
            "series_folder",
        ]:
            d[fp_key] = Path(d[fp_key])

        return cls(**d)

    @classmethod
    def load_toml(cls, fp: Path) -> "Config":
        data = toml.loads(fp.read_text())
        return cls.load(data)
