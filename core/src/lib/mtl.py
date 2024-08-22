import traceback

from llama_cpp import Llama

from .config import Config
from .db.mtl_cache import insert_translation, load_mtl_cache
from .db.reader_db import ReaderDb, load_reader_db
from .job_utils import JobManager, start_job_worker

_SYSTEM_PROMPT = """
I am a Korean to English translator. I will respond as concisely as possible.

Given a translation request, I will first answer with the English translation. 
And on the following lines I will provide a short mini-translation of each individual word.

I will NOT provide any additional commentary like "This is a complex sentence" or "This may be incorrect".
I will also NOT split any words or particles in my mini-translation. For example, if "역은" is a word in the sentence, I will not provide separate mini-translations for "역" and "은".

For example, if I am asked to "translate 안녕 내 이름은 제이크야", my response will follow this specific structure:

Hello, my name is Jake

- 안녕 = hello
- 내 = name
- 이름은 = name
- 제이크야 = is jake
""".strip()

_JOB_TYPE = "mtl"


def insert_mtl_job(db: ReaderDb, text: str):
    print("Inserting mtl job for", text)

    jobber = JobManager(db, _JOB_TYPE)
    jobber.insert(text, dict(text=text))
    db.commit()


def start_mtl_job_worker(cfg: Config):
    start_job_worker(
        cfg,
        _JOB_TYPE,
        _process_all_jobs,
        initializer=_init_worker,
        initargs=(cfg,),
    )


def _process_all_jobs(cfg: Config, job_ids: list[str]):
    reader_db = load_reader_db()
    jobber = JobManager(reader_db, _JOB_TYPE)

    for id in job_ids:
        try:
            _process_job(
                jobber,
                _WORKER_LLM,
                id,
            )
        except:
            # Delete job on error
            traceback.print_exc()

            jobber.delete(id)
            reader_db.commit()

            raise


_WORKER_LLM: Llama = None  # type: ignore


def _init_worker(cfg: Config):
    global _WORKER_LLM
    _WORKER_LLM = Llama.from_pretrained(
        cfg.llm_model_id,
        cfg.llm_model_file,
    )


def _process_job(
    jobber: JobManager,
    llm: Llama,
    job_id: str,
):
    # Get job data
    job = jobber.select(job_id)
    print("Processing mtl job", job_id, job["text"])

    translation = _mtl(llm, job["text"])

    cache = load_mtl_cache()
    insert_translation(cache, job["text"], translation)
    cache.commit()


def _mtl(llm: Llama, text: str) -> str:
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": _SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"Translate {text.strip()}",
            },
        ]
    )

    return output["choices"][0]["message"]["content"]  # type: ignore


def parse_mtl(text: str) -> dict | None:
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    if not lines:
        return None

    translation = lines.pop(0)

    words = dict()
    for ln in lines:
        ln = ln.strip("-").strip()

        split = ln.split("=", maxsplit=1)
        if len(split) <= 1:
            continue

        word, explanation = split
        words[word.strip()] = explanation.strip()

    return dict(
        translation=translation,
        words=words,
    )
