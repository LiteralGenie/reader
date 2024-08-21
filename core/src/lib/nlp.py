from jamo import h2j, j2hcj
from konlpy.tag import Kkma
from nltk import edit_distance

from .db.dictionary_db import load_dictionary_db, select_examples, select_words


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


def get_examples(word: str, kkma_pos: str) -> list[dict]:
    db = load_dictionary_db()

    check_ending = kkma_pos.startswith("J")
    check_verb = kkma_pos.startswith("V")
    matches = select_words(
        db,
        word,
        check_ending=check_ending,
        check_verb=check_verb,
    )

    words = list(set(m["word"] for m in matches))
    words.sort(key=lambda w: edit_distance(word, w))

    examples = []
    for w in words:
        examples.extend(select_examples(db, w))

    return examples


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
