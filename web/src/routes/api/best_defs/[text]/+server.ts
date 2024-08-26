import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ params }) => {
    // @ts-ignore
    const url = env.config.apiUrl + `/best_defs/${euc(params.text)}`
    return await fetch(url)
}
