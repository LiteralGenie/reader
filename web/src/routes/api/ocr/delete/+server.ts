import { env } from '$env/dynamic/private'
import type { RequestHandler } from './sse/$types'

export const POST: RequestHandler = async ({ request }) => {
    // @ts-ignore
    const apiUrl = new URL(env.config.apiUrl + '/ocr/delete')

    return await fetch(apiUrl, {
        method: 'POST',
        body: await request.text(),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}
