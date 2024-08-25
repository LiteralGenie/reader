import { env } from '$env/dynamic/private'
import { error } from '@sveltejs/kit'
import type { OcrMatchDto, OcrPageDto } from './dtos'

export async function fetchAllOcrData(
    series: string,
    chapter: string
): Promise<Record<string, OcrMatchDto[] | null>> {
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
): Promise<OcrPageDto | null> {
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
