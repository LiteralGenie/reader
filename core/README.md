mvp features:

    - ocr text
    - vocab breakdown
    - import / export detection data

bonus features:

    - manually edit detected text
    - configurable detection settings
    - MTL

dream:

    - custom models for panel detection / bubble detection / ocr
        - dataset can probably be auto-generated
        - allows better transcript ordering and text replacement

---

pipeline:

    - generate config
        - user inputs vauge series-specific / chapter-specific settings
        - translate these to settings actionable per-page
    - detect text
    - detect vocab
        - tokenize
        - get dictionary defs

data format:

    - raw ocr info
        - likely need per-character coords but pre-tokenized info is okay too
    - token info
        - coords
        - text
