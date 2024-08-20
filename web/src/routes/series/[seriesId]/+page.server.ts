import { fetchSeriesById } from '$lib/api/series'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ params }) => {
    const series = await fetchSeriesById(params.seriesId)

    return {
        series
    }
}
