import { fetchAllOcrData } from '$lib/api/ocr'
import { fetchChapterById } from '$lib/api/series'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ params }) => {
    const pages = await fetchChapterById(
        params.seriesId,
        params.chapterId
    )

    const ocrData = await fetchAllOcrData(
        params.seriesId,
        params.chapterId
    )

    return {
        pages,
        ocrData
    }
}
