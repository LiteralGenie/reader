import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ params }) => {
    // @ts-ignore
    const url = env.config.apiUrl + `/examples/${euc(params.text)}`

    return await fetch(url)
}
