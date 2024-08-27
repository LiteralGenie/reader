import { fetchAllSeries } from '$lib/api/series'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async () => {
    return {
        series: await fetchAllSeries()
    }
}
