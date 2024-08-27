import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils'
import { error } from '@sveltejs/kit'
import type {
    PageDto,
    SeriesDto,
    SeriesWithChaptersDto
} from './dtos'

export async function fetchAllSeries(): Promise<SeriesDto[]> {
    // @ts-ignore
    const url = env.config.apiUrl + '/series'
    const data = await (await fetch(url)).json()
    return data
}

export async function fetchSeriesById(
    series: string
): Promise<SeriesWithChaptersDto> {
    // @ts-ignore
    const url = env.config.apiUrl + `/series/${euc(series)}`

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
    const url =
        // @ts-ignore
        env.config.apiUrl + `/series/${euc(series)}/${euc(chapter)}`

    const resp = await fetch(url)
    if (resp.status !== 200) {
        throw error(404, 'Not Found')
    }

    const data = await resp.json()
    return data
}
