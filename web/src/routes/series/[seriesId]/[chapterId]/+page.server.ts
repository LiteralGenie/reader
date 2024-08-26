import { fetchAllOcrData } from '$lib/api/ocr'
import { fetchChapterById, fetchSeriesById } from '$lib/api/series'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ params }) => {
    const series = await fetchSeriesById(params.seriesId)

    const pages = await fetchChapterById(
        params.seriesId,
        params.chapterId
    )

    const ocrData = await fetchAllOcrData(
        params.seriesId,
        params.chapterId
    )

    return {
        series,
        pages,
        ocrData
    }
}
