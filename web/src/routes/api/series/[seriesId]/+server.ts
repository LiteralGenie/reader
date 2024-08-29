import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ request, url }) => {
    const proxyPath = url.pathname.replace('api/', '')

    const apiUrl = new URL(
        // @ts-ignore
        env.config.apiUrl + proxyPath
    )

    return await fetch(apiUrl, {
        method: request.method
    })
}
