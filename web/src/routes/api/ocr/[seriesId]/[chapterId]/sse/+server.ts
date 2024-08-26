import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ params, url }) => {
    const apiUrl = new URL(
        // @ts-ignore
        env.config.apiUrl +
            `/ocr/${euc(params.seriesId)}/${euc(params.chapterId)}/sse`
    )

    apiUrl.search = url.search

    return await fetch(apiUrl)
}
