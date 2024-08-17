from dataclasses import dataclass
from pathlib import Path

import toml


@dataclass
class Config:
    series_folder: Path

    api: "ApiConfig"

    @classmethod
    def load(cls, data: dict) -> "Config":
        d = data.copy()

        d["api"] = ApiConfig.load(d["api"])

        for fp_key in [
            "series_folder",
        ]:
            d[fp_key] = Path(d[fp_key])

        return cls(**d)

    @classmethod
    def load_toml(cls, fp: Path) -> "Config":
        data = toml.loads(fp.read_text())
        return cls.load(data)


@dataclass
class ApiConfig:
    port: int

    @classmethod
    def load(cls, data: dict) -> "ApiConfig":
        d = data.copy()

        for fp_key in []:
            d[fp_key] = Path(d[fp_key])

        return cls(**d)
