import re

from konlpy.tag import Kkma
from llama_cpp import Llama

from ..nlp import get_defs, get_pos_by_word, get_pos_by_word_dumb

_SYSTEM_PROMPT = """
I am a Korean to English translator whose specialty is picking the most relevant definition for a word.

I will pick ONLY the number of the definition.
I will NOT provide any additional commentary like "This is a complex sentence" or "This may be incorrect".

An example request and response is given below

Request:
```
Given this sentence:
아린성계 제 7 콜로니 아린의 바같에 위치한 자원행성 쿠란성의 근방에 지어진 게이트의 근처에 지어져있다

the word 지어진 can be broken into
지어진 = 짓 + 어 + 지 + ㄴ

"어" is a connective ending.
From the list below, pick the most relevant definition for "어"

0) 어 (suffix) = language, lect
1) -어 (suffix) = Marks the hortative mood.
2) -어 (suffix) = since, because; expresses causation.
3) -어 (suffix) = Marks the declarative or indicative mood.
4) -어 (suffix) = Joins the main verb or adjective to its auxiliary.
5) -어 (suffix) = The "infinitive" suffix, connecting verbs and adjectives.
6) -어 (suffix) = In the "intimate" speech level used between friends, by superiors to inferiors, ...
8) 어 (intj) = uh-huh, yes
9) 어 (intj) = ah!, oh!; conveys surprise, urgency, or strong emotion
10) 어근 (noun) = root
```

My response:
4
""".strip()

_REQUEST_TEMPLATE = """
Given this sentence:
{{ SENTENCE }}

the word {{ WORD }} can be broken into
{{ BREAKDOWN }}

{{ TARGET_POS }}
From the list below, pick the most relevant definition for "{{ TARGET }}"

{{ DEFN_LIST }}
""".strip()


def get_best_defs(llm: Llama, text: str, n_per_part=2) -> list[list[list[int]]]:
    kkma = Kkma()

    words = get_pos_by_word(kkma, text)
    if not words:
        words = get_pos_by_word_dumb(kkma, text)

    by_word: list[list[list[int]]] = []
    for w in words:
        by_part: list[list[int]] = []

        word_text = "".join(pt["text"] for pt in w)

        for part in w:
            id_best = _get_n_best_defs(
                llm,
                n_per_part,
                text,
                word_text,
                w,
                part,
            )
            by_part.append(id_best)

        by_word.append(by_part)

    return by_word


def _get_n_best_defs(
    llm: Llama,
    n: int,
    text: str,
    word: str,
    all_parts: list[dict],
    part: dict,
) -> list[int]:
    best = []

    defs = get_defs(part["text"], part["pos"])

    rem = defs.copy()
    for idx_try in range(n):
        if not rem:
            return best

        req = _format_request(
            text,
            word,
            part,
            all_parts,
            rem,
        )
        print("req", req)

        output = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": req},
            ]
        )
        content: str = output["choices"][0]["message"]["content"]  # type: ignore

        idx_selection = _extract_selection(content)
        if idx_selection is None:
            continue
        if idx_selection >= len(rem):
            continue

        defn = rem.pop(idx_selection)
        print("defn", idx_selection, defn)
        best.append(defn["id"])

    return best


def _format_request(
    text: str,
    word: str,
    part: dict,
    all_parts: list[dict],
    defs: list[dict],
):
    all_parts_str = " + ".join(pt["text"] for pt in all_parts)
    breakdown = f"{word} = {all_parts_str}"

    pos = _prettify_kkma_pos(part["pos"])
    if pos:
        target_pos = f'"{part["text"]}" is a {pos}.'
    else:
        target_pos = ""

    defn_list = _format_definition_list(defs)

    req = (
        _REQUEST_TEMPLATE.replace("{{ SENTENCE }}", text)
        .replace("{{ WORD }}", word)
        .replace("{{ BREAKDOWN }}", breakdown)
        .replace("{{ TARGET }}", part["text"])
        .replace("{{ TARGET_POS }}", target_pos)
        .replace("{{ DEFN_LIST }}", defn_list)
    )

    return req


def _format_definition_list(
    defs: list[dict],
    max_line_len=150,
    max_total_len=1000,
):
    total_len = 0

    lines = []
    for idx, d in enumerate(defs):
        pos = _prettify_kkma_pos(d["pos"])
        pos = f" ({pos})" if pos else ""

        defn = d["definition"]
        if len(defn) > max_line_len:
            defn = defn[: max_line_len - 3] + "..."

        ln = f"{idx}) {d['word']}{pos} = {defn}"
        lines.append(ln)

        total_len += len(ln)
        if total_len >= max_total_len:
            break

    return "\n".join(lines)


def _prettify_kkma_pos(kkma_pos: str) -> str:
    match kkma_pos:
        case "NNG":
            return "noun"
        case "NNP":
            "noun"
        case "NNB":
            "noun"
        case "NNM":
            "noun"
        case "NR":
            "noun"
        case "NP":
            "noun"
        case "VV":
            "verb"
        case "VCP":
            "verb"
        case "VCN":
            "verb"
        case "VA":
            return "adjective"
        case "VXV":
            return "auxillary verb"
        case "VXA":
            return "auxillary adjective"
        case "MDN":
            return "determiner"
        case "MDT":
            return "determiner"
        case "MAG":
            return "adverb"
        case "MAC":
            return "conjunction"
        case "IC":
            return "exclamation"
        case "JKS":
            return "particle"
        case "JKC":
            return "particle"
        case "JKG":
            return "particle"
        case "JKO":
            return "particle"
        case "JKM":
            return "particle"
        case "JKI":
            return "particle"
        case "JKQ":
            return "particle"
        case "JC":
            return "particle"
        case "JX":
            return "particle"
        case "EPH":
            return "verb ending"
        case "EPT":
            return "verb ending"
        case "EPP":
            return "verb ending"
        case "EFN":
            return "verb ending"
        case "EFQ":
            return "verb ending"
        case "EFO":
            return "verb ending"
        case "EFA":
            return "verb ending"
        case "EFI":
            return "verb ending"
        case "EFR":
            return "verb ending"
        case "ECE":
            return "verb ending"
        case "ECS":
            return "verb ending"
        case "ECD":
            return "verb ending"
        case "ETN":
            return "verb ending"
        case "ETD":
            return "verb ending"
        case "XPN":
            return "prefix"
        case "XPV":
            return "verb prefix"
        case "XSN":
            return "suffix"
        case "XSV":
            return "verb suffix"
        case "XSA":
            return "adjective suffix"
        case "XR":
            return "word stem"
        case "SF":
            return "punctuation"
        case "SE":
            return "punctuation"
        case "SS":
            return "punctuation"
        case "SP":
            return "punctuation"
        case "SO":
            return "punctuation"
        case "SW":
            return "punctuation"
        case "OH":
            return "hanja"
        case "OL":
            return "loan word"
        case "ON":
            return "number"
        case "UN":
            return ""

    return ""


def _extract_selection(output: str) -> int | None:
    m = re.search(r"(\d+)", output)
    if not m:
        return None

    return int(m.group(1))
