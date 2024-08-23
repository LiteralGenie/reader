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
    id: number
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
    id: number
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

export type BestDefDto = number[][][]
