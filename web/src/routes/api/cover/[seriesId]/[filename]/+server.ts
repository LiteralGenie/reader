import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils'
import type { RequestHandler } from '@sveltejs/kit'

export const GET: RequestHandler = async ({ params }) => {
    const url =
        // @ts-ignore
        env.config.apiUrl +
        `/cover/${euc(params.seriesId)}/${euc(params.filename)}`
    return await fetch(url)
}
