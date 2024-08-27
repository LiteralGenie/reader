import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from ..lib.config import Config

CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "config.toml"

DESCRIPTION = """
Downloads all images from a given URL the root_image_folder your config.toml 

For example, this command:

    python core/src/scripts/download_images.py https://abc.xyz/read/chap_1/ wowow 001

will download all images to data/series/wowow/001/
(assuming you're using the default root_image_folder
""".strip()


def run(args):
    pass


def _parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument("url")
    parser.add_argument("series_folder")
    parser.add_argument("chapter_folder")

    parser.add_argument(
        "--delay",
        type=int,
        default=0.25,
        help="Delay in seconds between requests",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    cfg = Config.load_toml(CONFIG_FILE)

    run(args)
