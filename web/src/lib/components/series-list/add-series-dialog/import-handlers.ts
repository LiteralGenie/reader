import type { SeriesDto } from '$lib/api/dtos'
import { throwOnStatus } from '$lib/miscUtils'
import sanitize from 'sanitize-filename'

export async function importMangadexSeries(id: string) {
    // Get series info
    const infoResp = await fetch(`/api/proxy/mangadex/manga/${id}`)
    throwOnStatus(infoResp)
    const info = await infoResp.json()
    console.log('Fetched series info', info)

    // Calculate title
    let title = info?.data?.attributes?.title?.en as
        | string
        | undefined
    title = title ?? id

    // Calculate folder name
    const series: SeriesDto[] = await (
        await fetch('/api/series')
    ).json()
    const filename = addSuffixUntilUnique(series, title)

    // Get cover image
    const coverBytes = await fetchMdCover(id, info)

    // Submit
    const formData = new FormData()
    formData.set('filename', filename)
    formData.set('name', title)

    if (coverBytes) {
        const blob = new Blob([coverBytes])
        formData.set('cover', blob)
    }

    const resp = await fetch('/api/series', {
        method: 'POST',
        body: formData
    })
    throwOnStatus(resp)

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

    const imResp = await fetch(
        `/api/proxy/mangadex_cover/${id}/${fileName}`
    )
    console.log('Fetched cover image', imResp)
    throwOnStatus(imResp)
    const imBytes = await imResp.arrayBuffer()
    return imBytes
}

export function addSuffixUntilUnique(
    allSeries: SeriesDto[],
    base: string
) {
    const baseFilename = sanitize(base)
    let nameIdx = 2

    let filename = baseFilename
    while (allSeries.some((s) => s.filename === filename)) {
        filename = `${baseFilename}_${nameIdx}`
        nameIdx += 1
    }

    return filename
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

    const filename = addSuffixUntilUnique(series, name)

    // Send request
    const postData = new FormData()
    postData.set('filename', filename)
    postData.set('name', name)

    const cover = data.get('cover') as File
    if (cover.size > 0) {
        postData.set('cover', cover)
    }

    const resp = await fetch('/api/series', {
        method: 'POST',
        body: postData
    })
    throwOnStatus(resp)

    return filename
}
