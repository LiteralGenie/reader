export interface SeriesDto {
    filename: string
    name: string
    id_mangaupdates: string
    id_mangadex: string
    cover: string | null
    num_chapters: number
}

export interface ChapterDto {
    filename: string
    name: string
    num_pages: number
}

export interface PageDto {
    filename: string
    sha256: string
    width: number
    height: number
}

export type SeriesWithChaptersDto = SeriesDto & {
    chapters: ChapterDto[]
}

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

export interface PartialNlpDto {
    text: string
    pos: string
}

export interface DefDto {
    id: number
    word: string
    pos: string
    definition: string
}

export type OcrPageDto = Record<string, OcrMatchDto>

export interface OcrMatchDto {
    id: string
    bbox: Bbox
    confidence: number
    value: string
}

export type Bbox = [number, number, number, number]

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

export interface PartialDefinition {
    text: string
    definitions: DefinitionDto[]
}
