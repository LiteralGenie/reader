from llama_cpp import Llama

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


def mtl(llm: Llama, text: str) -> str:
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

    return output["choices"][0]["message"]["content"].strip()  # type: ignore


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
