import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ params }) => {
    const url = new URL(
        // @ts-ignore
        env.config.apiUrl + `/chunk/${params.word}`
    )

    return await fetch(url)
}
