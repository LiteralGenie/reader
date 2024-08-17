import { fetchChapterById } from '$lib/api/series'
import { error } from '@sveltejs/kit'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ params }) => {
    const chapter = await fetchChapterById(
        params.seriesId,
        params.chapterId
    )
    if (!chapter) throw error(404, 'Not Found')

    return {
        chapter
    }
}
