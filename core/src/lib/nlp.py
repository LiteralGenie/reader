import multiprocessing
from multiprocessing.pool import Pool

from konlpy.tag import Kkma
from lib.misc_utils import to_jamo
from nltk import edit_distance

from .db.dictionary_db import load_dictionary_db, select_words


def get_pos_by_word(tagger: Kkma | Pool, text: str) -> list[list[dict]] | None:
    if isinstance(tagger, Kkma):
        all_pos = tagger.pos(text)
    else:
        all_pos = tagger.apply(_pool_pos, [text])

    words = text.split()

    try:
        pos_by_word: list[list[dict]] = []

        rem_pos = all_pos.copy()
        for w in words:
            parts: list[dict] = []

            rem_jamo = to_jamo(w)
            while rem_jamo:
                chars, tag = rem_pos.pop(0)
                chars_jamo = to_jamo(chars)

                assert (
                    rem_jamo[: len(chars_jamo)] == chars_jamo
                ), f"{all_pos} {[to_jamo(w) for w in words]}"

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


def get_pos_by_word_dumb(tagger: Pool | Kkma, text: str) -> list[list[dict]]:
    pos_by_word = []

    words = text.split()
    for w in words:
        parts = []

        if isinstance(tagger, Kkma):
            pos = tagger.pos(w)
        else:
            pos = tagger.apply(_pool_pos, [w])

        for chars, tag in pos:
            parts.append(
                dict(
                    text=chars,
                    pos=tag,
                )
            )

        pos_by_word.append(parts)

    return pos_by_word


def get_defs(word: str, kkma_pos: str) -> list[dict]:
    db = load_dictionary_db()

    check_dash_prefix = kkma_pos.startswith("J") or kkma_pos.startswith("E")
    check_suffix = (
        kkma_pos.startswith("V")
        or kkma_pos in ["XSV", "XSA"]
        or kkma_pos.startswith("E")
    )
    matches = select_words(
        db,
        word,
        check_dash_prefix=check_dash_prefix,
        check_suffix=check_suffix,
    )

    matches.sort(key=lambda d: _score_definition_match(word, kkma_pos, d))

    return matches


def _score_definition_match(text: str, kkma_pos: str, data: dict):
    char_dist = edit_distance(text, data["word"])

    # @TODO: wiktionary pos:
    # character, symbol, noun, intj, root, name, num, verb, syllable, det, prefix, suffix, affix, particle, adv, pron, adj, counter, phrase, punct, proverb, interfix, romanization, conj

    pos_dist = float("inf")
    if kkma_pos.startswith("J"):
        # particles
        match data["pos"]:
            case "particle":
                pos_dist = 0
            case "suffix":
                pos_dist = 1
            case "affix":
                pos_dist = 2
    elif kkma_pos in ["VA", "VXA"]:
        # adjectives
        match data["pos"]:
            case "adj":
                pos_dist = 0
    elif kkma_pos in ["VV", "VCP", "VCN", "VXV"]:
        # verbs
        match data["pos"]:
            case "verb":
                pos_dist = 0
    elif kkma_pos in ["MAG"]:
        # adverbs
        match data["pos"]:
            case "adv":
                pos_dist = 0
    elif kkma_pos in ["XSV"]:
        # verb suffixes (eg 하다)
        match data["pos"]:
            case "suffix":
                pos_dist = 0
            case "affix":
                pos_dist = 1
            case "verb":
                pos_dist = 2
            case "particle":
                pos_dist = 3
    elif kkma_pos in ["XSA"]:
        # adjective suffixes
        match data["pos"]:
            case "suffix":
                pos_dist = 0
            case "affix":
                pos_dist = 1
            case "adj":
                pos_dist = 2
            case "particle":
                pos_dist = 3
    elif kkma_pos in ["XSN"]:
        # noun suffixes
        match data["pos"]:
            case "suffix":
                pos_dist = 0
            case "particle":
                pos_dist = 1
            case "affix":
                pos_dist = 2
    elif kkma_pos.startswith("E"):
        # connective particles (eg -어(지다))
        match data["pos"]:
            case "suffix":
                pos_dist = 0
            case "prefix":
                pos_dist = 0
            case "affix":
                pos_dist = 0
            case "particle":
                pos_dist = 1

    length = len(data["definition"])

    return (pos_dist, char_dist, length)


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
