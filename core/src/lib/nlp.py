from jamo import h2j, j2hcj
from konlpy.tag import Kkma
from nltk import edit_distance

from .db.wiktionary_db import (
    load_wiktionary_db,
    select_exact_matches,
    select_partial_matches,
)


def get_pos_by_word(kkma: Kkma, text: str) -> list[list[dict]]:
    all_pos = kkma.pos(text)
    words = text.split()

    pos_by_word: list[list[dict]] = []

    rem_pos = all_pos.copy()
    for w in words:
        parts: list[dict] = []

        rem_jamo = _to_jamo(w)
        while rem_jamo:
            text, tag = rem_pos.pop(0)
            text_jamo = _to_jamo(text)

            assert rem_jamo[: len(text_jamo)] == text_jamo, f"{rem_jamo} {text_jamo}"

            parts.append(
                dict(
                    text=text,
                    pos=tag,
                )
            )

            rem_jamo = rem_jamo[len(text_jamo) :]

        pos_by_word.append(parts)

    return pos_by_word


def _to_jamo(text: str) -> list[str]:
    return [char for char in j2hcj(h2j(text))]


def get_wikti_defs(word: str, kkma_pos=""):
    db = load_wiktionary_db()

    check_ending = kkma_pos.startswith("J")
    check_verb = kkma_pos.startswith("V")
    matches = select_exact_matches(
        db,
        word,
        check_ending=check_ending,
        check_verb=check_verb,
    )
    # if not matches:
    #     matches = select_partial_matches(db, word)

    matches.sort(key=lambda d: _score_match(word, kkma_pos, d))

    seen = set()

    defs = []
    for m in matches:
        for sense in m["senses"]:
            for gloss in sense["glosses"]:
                if gloss in seen:
                    continue
                else:
                    seen.add(gloss)

                defs.append(
                    dict(
                        stem=m["word"],
                        definition=gloss,
                        pos=m["pos"],
                    )
                )

    return defs


def _score_match(text: str, kkma_pos: str, wiki_data: dict):
    char_dist = edit_distance(text, wiki_data["word"])

    pos_dist = float("inf")
    if kkma_pos.startswith("J"):
        match wiki_data["pos"]:
            case "particle":
                pos_dist = 0
            case "suffix":
                pos_dist = 1

    return (pos_dist, char_dist)
