import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils.js'

export async function GET({ params }) {
    const url =
        // @ts-ignore
        env.config.apiUrl +
        `/series/${euc(params.seriesId)}/${euc(params.chapterId)}/${euc(params.pageId)}`
    const resp = await fetch(url)
    const data = await resp.blob()
    return new Response(data)
}
