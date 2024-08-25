import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const PATCH: RequestHandler = async ({ request }) => {
    // @ts-ignore
    const apiUrl = new URL(env.config.apiUrl + '/ocr/text')

    return await fetch(apiUrl, {
        method: 'PATCH',
        body: await request.text(),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}
