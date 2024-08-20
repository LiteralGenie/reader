import { env } from '$env/dynamic/private'
import { error } from '@sveltejs/kit'

export interface OcrMatch {
    bbox: [number, number, number, number]
    confidence: number
    value: string
}

export async function fetchAllOcrData(
    series: string,
    chapter: string
): Promise<Record<string, OcrMatch[] | null>> {
    const url =
        // @ts-ignore
        env.config.apiUrl + `/ocr/${series}/${chapter}/`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        throw error(404, 'Not Found')
    }

    const data = await resp.json()
    return data
}

export async function fetchOcrData(
    series: string,
    chapter: string,
    page: string
): Promise<OcrMatch[] | null> {
    const url =
        // @ts-ignore
        env.config.apiUrl + `/ocr/${series}/${chapter}/${page}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        throw error(404, 'Not Found')
    }

    const data = await resp.json()
    return data
}
