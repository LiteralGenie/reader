import loguru

from ..paths import LOG_DIR

loguru.logger.add(
    LOG_DIR / "llm.log",
    level="INFO",
    filter=lambda record: record["extra"].get("name") == "llm",
    rotation="10 MB",
    retention=2,
)
LLM_LOGGER = loguru.logger.bind(name="llm")
