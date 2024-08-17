import { fetchSeriesById } from '$lib/api/series'
import { error } from '@sveltejs/kit'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ params }) => {
    const series = await fetchSeriesById(params.seriesId)
    if (!series) throw error(404, 'Not Found')

    return {
        series
    }
}
