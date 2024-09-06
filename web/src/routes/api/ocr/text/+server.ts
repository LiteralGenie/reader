import { proxyApiRequest } from '$lib/proxy'
import type { RequestHandler } from './$types'

export const PATCH: RequestHandler = async ({
    request,
    url,
    getClientAddress
}) => {
    return proxyApiRequest(request, url, getClientAddress(), {
        bodyType: 'JSON'
    })
}
