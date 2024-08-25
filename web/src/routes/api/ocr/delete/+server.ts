import { env } from '$env/dynamic/private'
import type { RequestHandler } from './$types'

export const DELETE: RequestHandler = async ({ request }) => {
    // @ts-ignore
    const apiUrl = new URL(env.config.apiUrl + '/ocr/delete')

    return await fetch(apiUrl, {
        method: 'DELETE',
        body: await request.text(),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}
