import { env } from '$env/dynamic/private'

export async function GET({ params }) {
    const url =
        // @ts-ignore
        env.config.apiUrl +
        `/series/${params.seriesId}/${params.chapterId}/${params.pageId}`
    const resp = await fetch(url)
    const data = await resp.blob()
    return new Response(data)
}
