import { env } from '$env/dynamic/private'

export interface SeriesDto {
    name: string
    chapters: ChapterDto[]
}

export interface ChapterDto {
    name: string
    has_ocr_data: boolean
    pages: PageDto[]
}

export interface PageDto {
    filename: string
    matches: MatchDto[]
}

export interface MatchDto {
    id: string
    bbox: [number, number, number, number]
    confidence: number
    value: string
}

export async function fetchAllSeries(): Promise<SeriesDto[]> {
    // @ts-ignore
    const url = env.config.apiUrl + '/series'
    const data: SeriesDto[] = await (await fetch(url)).json()
    return data
}

export async function fetchSeriesById(
    series: string
): Promise<SeriesDto | null> {
    // @ts-ignore
    const url = env.config.apiUrl + `/series/${series}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        return null
    }

    const data: SeriesDto = await resp.json()
    return data
}

export async function fetchChapterById(
    series: string,
    chapter: string
): Promise<ChapterDto | null> {
    // @ts-ignore
    const url = env.config.apiUrl + `/series/${series}/${chapter}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        return null
    }

    const data: ChapterDto = await resp.json()
    return data
}
