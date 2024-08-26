import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils'
import { error } from '@sveltejs/kit'
import type { OcrPageDto } from './dtos'

export async function fetchAllOcrData(
    series: string,
    chapter: string
): Promise<Record<string, OcrPageDto | null>> {
    const url =
        // @ts-ignore
        env.config.apiUrl + `/ocr/${euc(series)}/${euc(chapter)}/`

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
): Promise<OcrPageDto | null> {
    const url =
        // @ts-ignore
        env.config.apiUrl +
        `/ocr/${euc(series)}/${chapter}/${euc(page)}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        throw error(404, 'Not Found')
    }

    const data = await resp.json()
    return data
}
