import { proxyApiRequest } from '$lib/proxy'
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({
    request,
    url,
    getClientAddress
}) => {
    return proxyApiRequest(request, url, getClientAddress())
}
