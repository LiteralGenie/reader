import { env } from '$env/dynamic/private'
import { error } from '@sveltejs/kit'
import type { ChapterDto, PageDto, SeriesDto } from './dtos'

export async function fetchAllSeries(): Promise<SeriesDto[]> {
    // @ts-ignore
    const url = env.config.apiUrl + '/series'
    const data = await (await fetch(url)).json()
    return data
}

export async function fetchSeriesById(
    series: string
): Promise<ChapterDto[]> {
    // @ts-ignore
    const url = env.config.apiUrl + `/series/${series}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        throw error(404, 'Not Found')
    }

    const data = await resp.json()
    return data
}

export async function fetchChapterById(
    series: string,
    chapter: string
): Promise<PageDto[]> {
    // @ts-ignore
    const url = env.config.apiUrl + `/series/${series}/${chapter}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        throw error(404, 'Not Found')
    }

    const data = await resp.json()
    return data
}
