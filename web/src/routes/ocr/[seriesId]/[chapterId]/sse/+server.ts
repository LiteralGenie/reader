import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ params, url }) => {
    const apiUrl = new URL(
        // @ts-ignore
        env.config.apiUrl +
            `/ocr/${params.seriesId}/${params.chapterId}/sse`
    )

    apiUrl.search = url.search

    return await fetch(apiUrl)
}
