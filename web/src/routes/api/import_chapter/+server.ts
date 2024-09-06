import { proxyApiRequest } from '$lib/proxy'
import type { RequestHandler } from '@sveltejs/kit'

export const POST: RequestHandler = async ({
    request,
    url,
    getClientAddress
}) => {
    return proxyApiRequest(request, url, getClientAddress(), {
        bodyType: 'JSON'
    })
}
