import type { SeriesDto } from '$lib/api/dtos'
import { addSuffixUntilUnique, throwOnStatus } from '$lib/miscUtils'

export interface ImportedSeries {
    filename: string
    name: string
    cover?: File | null
    mangaDexId?: string | null
    mangaUpdatesId?: string | null
}

export async function postSeries(data: ImportedSeries) {
    const formData = new FormData()
    formData.set('filename', data.filename)
    formData.set('name', data.name)

    if (data.cover && data.cover.size > 0) {
        formData.set('cover', data.cover)
    }

    if (data.mangaDexId) {
        formData.set('id_mangadex', data.mangaDexId)
    }

    if (data.mangaUpdatesId) {
        formData.set('id_mangadex', data.mangaUpdatesId)
    }

    const resp = await fetch('/api/series', {
        method: 'POST',
        body: formData
    })
    await throwOnStatus(resp)

    return resp
}

export async function importMangaDexSeries(maybeId: string) {
    const patt = new RegExp('mangadex.org/title/([a-z0-9-]+)', 'i')
    const id = maybeId.match(patt)?.[1] ?? maybeId

    // Get series info
    const infoResp = await fetch(`/api/proxy/mangadex/manga/${id}`)
    await throwOnStatus(infoResp)
    const info = await infoResp.json()
    console.log('Fetched series info', info)

    // Calculate title
    let title = info?.data?.attributes?.title?.en as
        | string
        | undefined
    title = title || id

    // Calculate folder name
    const series: SeriesDto[] = await (
        await fetch('/api/series')
    ).json()
    const filename = addSuffixUntilUnique(
        series.map((s) => s.filename),
        title
    )

    // Get cover image
    const cover = await fetchMdCover(id, info)

    // Submit
    return {
        filename,
        name: title,
        cover,
        mangaDexId: id
    }
}

async function fetchMdCover(id: string, info: any) {
    const coverId = (info?.data?.relationships as any[])?.find(
        (d) => d.type === 'cover_art'
    )?.['id']
    if (!coverId) {
        return null
    }

    const coverInfoResp = await fetch(
        `/api/proxy/mangadex/cover/${coverId}`
    )
    await throwOnStatus(coverInfoResp)
    const coverInfo = await coverInfoResp.json()
    console.log('Fetched cover info', coverInfo)

    const fileName = coverInfo?.data?.attributes?.fileName
    if (!fileName) {
        return null
    }

    const file = await fetchImageFile(
        `/api/proxy/mangadex_cover/${id}/${fileName}`,
        fileName
    )
    return file
}

export async function importMangaUpdatesSeries(maybeId: string) {
    const patt = new RegExp(
        'mangaupdates.com/series/([a-z0-9-]+)',
        'i'
    )
    const id = maybeId.match(patt)?.[1] ?? maybeId

    // Get series info
    const realId = parseInt(id, 36)
    const infoResp = await fetch(
        `/api/proxy/mangaupdates/series/${realId}`
    )
    await throwOnStatus(infoResp)
    const info = await infoResp.json()
    console.log('Fetched series info', info)

    // Calculate title
    let title = info?.title as string | undefined
    title = title || id

    // Calculate folder name
    const series: SeriesDto[] = await (
        await fetch('/api/series')
    ).json()
    const filename = addSuffixUntilUnique(
        series.map((s) => s.filename),
        title
    )

    // Get cover image
    let cover: File | null = null
    const coverUrl = info?.image?.url?.original
    if (coverUrl) {
        const coverUrlObj = new URL(coverUrl)
        const proxyUrl =
            '/api/proxy/mangaupdates_cover' + coverUrlObj.pathname
        cover = await fetchImageFile(proxyUrl)
    }

    // Submit
    return {
        filename,
        name: title,
        cover,
        mangaUpdatesId: id
    }
}

async function fetchImageFile(
    url: string,
    filename?: string
): Promise<File> {
    const resp = await fetch(url)
    await throwOnStatus(resp)
    console.log('Fetched image', resp)

    const bytes = await resp.arrayBuffer()

    const contentType = resp.headers.get('Content-Type')

    if (!filename) {
        const disposition = resp.headers.get('Content-Disposition')
        if (disposition) {
            filename =
                disposition.match(/filename=".*"/)?.[1] || undefined
        }
    }

    const file = new File([bytes], filename || 'cover.png', {
        type: contentType ?? undefined
    })
    return file
}

export async function importManualSeries(data: FormData) {
    // Generate unique folder name
    const name = data.get('name')
    if (!name || typeof name !== 'string') {
        return
    }

    const series: SeriesDto[] = await (
        await fetch('/api/series')
    ).json()

    const filename = addSuffixUntilUnique(
        series.map((s) => s.filename),
        name
    )

    // Send request
    const resp = await postSeries({
        filename,
        name,
        cover: data.get('cover') as File
    })

    return filename
}
