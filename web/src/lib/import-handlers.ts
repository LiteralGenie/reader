import type { SeriesDto } from '$lib/api/dtos'
import { addSuffixUntilUnique, throwOnStatus } from '$lib/miscUtils'

export interface ImportedSeries {
    filename: string
    name: string
    coverBytes?: ArrayBuffer | null
    coverFile?: File | null
    mangaDexId?: string | null
    mangaUpdatesId?: string | null
}

export async function postSeries(data: ImportedSeries) {
    const formData = new FormData()
    formData.set('filename', data.filename)
    formData.set('name', data.name)

    if (data.coverBytes) {
        const blob = new Blob([data.coverBytes])
        formData.set('cover', blob)
    } else if (data.coverFile && data.coverFile.size > 0) {
        formData.set('cover', data.coverFile)
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
    throwOnStatus(resp)

    return resp
}

export async function importMangaDexSeries(maybeId: string) {
    const patt = new RegExp('mangadex.org/title/([a-z0-9-]+)', 'i')
    const id = maybeId.match(patt)?.[1] ?? maybeId

    // Get series info
    const infoResp = await fetch(`/api/proxy/mangadex/manga/${id}`)
    throwOnStatus(infoResp)
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
    const coverBytes = await fetchMdCover(id, info)

    // Submit
    return {
        filename,
        name: title,
        coverBytes: coverBytes,
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
    throwOnStatus(coverInfoResp)
    const coverInfo = await coverInfoResp.json()
    console.log('Fetched cover info', coverInfo)

    const fileName = coverInfo?.data?.attributes?.fileName
    if (!fileName) {
        return null
    }

    const imBytes = await fetchImageBytes(
        `/api/proxy/mangadex_cover/${id}/${fileName}`
    )
    return imBytes
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
    throwOnStatus(infoResp)
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
    const coverUrl = info?.image?.url?.original
    let coverBytes: ArrayBuffer | null = null
    if (coverUrl) {
        const coverUrlObj = new URL(coverUrl)
        const proxyUrl =
            '/api/proxy/mangaupdates_cover' + coverUrlObj.pathname
        coverBytes = await fetchImageBytes(proxyUrl)
    }

    // Submit
    return {
        filename,
        name: title,
        coverBytes: coverBytes,
        mangaUpdatesId: id
    }
}

async function fetchImageBytes(url: string) {
    const resp = await fetch(url)
    throwOnStatus(resp)
    console.log('Fetched image', resp)

    const imBytes = await resp.arrayBuffer()
    return imBytes
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
        coverFile: data.get('cover') as File
    })

    return filename
}
