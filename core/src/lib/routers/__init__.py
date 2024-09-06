import loguru

from ..paths import LOG_DIR

loguru.logger.add(
    LOG_DIR / "edits.log",
    filter=lambda record: record["extra"].get("name") == "edits",
    rotation="10 MB",
    retention=2,
)
EDIT_LOGGER = loguru.logger.bind(name="edits")
