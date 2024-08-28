import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const POST: RequestHandler = async ({ request }) => {
    // @ts-ignore
    const url = env.config.apiUrl + `/series`
    return await fetch(url, {
        method: request.method,
        body: await request.formData()
    })
}

export const GET: RequestHandler = async ({ request }) => {
    // @ts-ignore
    const url = env.config.apiUrl + `/series`
    return await fetch(url, {
        method: request.method,
        headers: request.headers
    })
}
