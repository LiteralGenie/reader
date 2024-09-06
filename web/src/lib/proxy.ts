import { env } from '$env/dynamic/private'

export interface ProxyRequestOpts {
    allHeaders?: boolean
    bodyType?: null | 'text' | 'JSON' | 'FormData'
    search?: string
}

export async function proxyApiRequest(
    request: Request,
    url: URL,
    source: string,
    opts?: ProxyRequestOpts
): Promise<Response> {
    let body: any | undefined = undefined
    let headers: Record<string, string> = {}

    if (opts?.allHeaders) {
        headers = Object.fromEntries(request.headers.entries())
    }

    headers['X-Forwarded-For'] = source

    switch (opts?.bodyType) {
        case 'text':
            body = await request.text()
            break
        case 'JSON':
            body = await request.text()
            headers['Content-Type'] = 'application/json'
            break
        case 'FormData':
            body = await request.formData()
            break
    }

    const proxyPath = url.pathname.replace('api/', '')
    const apiUrl = new URL(
        // @ts-ignore
        env.config.apiUrl + proxyPath
    )

    if (opts?.search) {
        apiUrl.search = opts.search
    }

    return fetch(apiUrl, {
        method: request.method,
        body,
        headers
    })
}
