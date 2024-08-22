import multiprocessing
from multiprocessing.pool import Pool

from jamo import h2j, j2hcj
from konlpy.tag import Kkma
from nltk import edit_distance

from .db.dictionary_db import load_dictionary_db, select_words


def get_pos_by_word(kkma_pool: Pool, text: str) -> list[list[dict]] | None:
    all_pos = kkma_pool.apply(_pool_pos, [text])
    words = text.split()

    try:
        pos_by_word: list[list[dict]] = []

        rem_pos = all_pos.copy()
        for w in words:
            parts: list[dict] = []

            rem_jamo = _to_jamo(w)
            while rem_jamo:
                chars, tag = rem_pos.pop(0)
                chars_jamo = _to_jamo(chars)

                assert (
                    rem_jamo[: len(chars_jamo)] == chars_jamo
                ), f"{all_pos} {[_to_jamo(w) for w in words]}"

                parts.append(
                    dict(
                        text=chars,
                        pos=tag,
                    )
                )

                rem_jamo = rem_jamo[len(chars_jamo) :]

            pos_by_word.append(parts)

        return pos_by_word
    except:
        print("Failed to map kkma parts to original text", text, all_pos)
        return None


def get_pos_by_word_dumb(kkma_pool: Pool, text: str) -> list[list[dict]]:
    pos_by_word = []

    words = text.split()
    for w in words:
        parts = []

        pos = kkma_pool.apply(_pool_pos, (w,))
        for chars, tag in pos:
            parts.append(
                dict(
                    text=chars,
                    pos=tag,
                )
            )

        pos_by_word.append(parts)

    return pos_by_word


def _to_jamo(text: str) -> list[str]:
    return [char for char in j2hcj(h2j(text))]


def get_defs(word: str, kkma_pos: str) -> list[dict]:
    db = load_dictionary_db()

    check_ending = kkma_pos.startswith("J")
    check_verb = kkma_pos.startswith("V")
    matches = select_words(
        db,
        word,
        check_ending=check_ending,
        check_verb=check_verb,
    )

    matches.sort(key=lambda d: _score_definition_match(word, kkma_pos, d))

    return matches


def _score_definition_match(text: str, kkma_pos: str, data: dict):
    char_dist = edit_distance(text, data["word"])

    pos_dist = float("inf")
    if kkma_pos.startswith("J"):
        match data["pos"]:
            case "particle":
                pos_dist = 0
            case "suffix":
                pos_dist = 1

    return (pos_dist, char_dist)


# We need to run the konlpy tagger in a pool
# because it will somehow break the llm inference if it's even initialized in the main process
# (causes the jinja2 templating during inference to hang without errors)
# ¯\_(ツ)_/¯
def start_nlp_pool():
    return multiprocessing.Pool(
        1,
        initializer=_init_pool_worker,
    )


_kkma: Kkma = None  # type: ignore


def _init_pool_worker():
    global _kkma
    _kkma = Kkma()

    _kkma.pos("안녕, 세상")  # warm up whatever caches


def _pool_pos(text: str):
    return _kkma.pos(text)
