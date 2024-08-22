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
