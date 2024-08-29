import type { SeriesDto } from '$lib/api/dtos'
import { addSuffixUntilUnique, throwOnStatus } from '$lib/miscUtils'

interface PostSeriesRequest {
    filename: string
    name: string
    coverBytes?: ArrayBuffer | null
    coverFile?: File | null
    mangaDexId?: string | null
    mangaUpdatesId?: string | null
}

async function postSeries(req: PostSeriesRequest) {
    const formData = new FormData()
    formData.set('filename', req.filename)
    formData.set('name', req.name)

    if (req.coverBytes) {
        const blob = new Blob([req.coverBytes])
        formData.set('cover', blob)
    } else if (req.coverFile && req.coverFile.size > 0) {
        formData.set('cover', req.coverFile)
    }

    if (req.mangaDexId) {
        formData.set('id_mangadex', req.mangaDexId)
    }

    if (req.mangaUpdatesId) {
        formData.set('id_mangadex', req.mangaUpdatesId)
    }

    const resp = await fetch('/api/series', {
        method: 'POST',
        body: formData
    })
    throwOnStatus(resp)

    return resp
}

export async function importMangaDexSeries(id: string) {
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
    const resp = await postSeries({
        filename,
        name: title,
        coverBytes: coverBytes,
        mangaDexId: id
    })

    return filename
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

export async function importMangaUpdatesSeries(id: string) {
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
    const resp = await postSeries({
        filename,
        name: title,
        coverBytes: coverBytes,
        mangaUpdatesId: id
    })

    return filename
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
