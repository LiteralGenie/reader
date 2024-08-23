export type JSONResponse<T> = Response & {
    json: () => Promise<T>
}

export interface MtlDto {
    translation: string
    words: Record<string, string>
}

export interface NlpDto {
    text: string
    pos: string
    defs: DefDto[]
}

export interface DefDto {
    word: string
    pos: string
    definition: string
}

export interface OcrMatch {
    bbox: [number, number, number, number]
    confidence: number
    value: string
}

export interface DefinitionDto {
    word: string
    pos: string
    definition: string
    source: string
}

export interface ExampleDto {
    korean: string
    english: string
    source: string
}
