import { proxyApiRequest } from '$lib/proxy'
import type { RequestHandler } from './$types'

export const DELETE: RequestHandler = async ({
    request,
    url,
    getClientAddress
}) => {
    return proxyApiRequest(request, url, getClientAddress(), {
        bodyType: 'JSON'
    })
}
