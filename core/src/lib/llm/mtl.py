import json

from llama_cpp import Llama

_SYSTEM_PROMPT = """
I am a Korean to English translator. I will respond as concisely as possible.

Given a translation request, I will provide a response in JSON format.
The response will have an entry for "translation" and an additional translation for each individual word under the "words" key.

I will NOT provide any additional commentary like "This is a complex sentence" or "This may be incorrect".
I will also NOT split any words or particles in my mini-translation. For example, if "역은" is a word in the sentence, I will not provide separate mini-translations for "역" and "은".

For example, if I am asked to "translate 안녕 내 이름은 제이크야", my response will follow this specific structure:

{
    "translation": "Hello, my name is Jake",
    "words": {
        "안녕": "hello",
        "내": "name",
        "이름은": "name",
        "제이크야": "is jake"
    }
}
""".strip()


def mtl(llm: Llama, text: str) -> dict:
    words = []
    for w in text.split():
        if w not in words:
            words.append(w)

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
        ],
        response_format={
            "type": "json_object",
            "schema": {
                "type": "object",
                "properties": {
                    "translation": {"type": "string"},
                    "words": {
                        "type": "object",
                        "properties": {w: {"type": "string"} for w in words},
                        "required": [w for w in words],
                    },
                },
                "required": ["translation", "words"],
            },
        },
    )

    resp = output["choices"][0]["message"]["content"].strip()  # type: ignore

    resp_data = json.loads(resp)
    return resp_data
