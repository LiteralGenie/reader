import { countExamples, fetchExamples } from '$lib/api/dictionary'
import { EXAMPLE_PAGE_SIZE } from '$lib/constants'
import { toJson } from '$lib/miscUtils'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ url, fetch }) => {
    const query = url.searchParams.get('query') ?? ''
    const idxPage = parseInt(url.searchParams.get('page') ?? '1') ?? 1

    const count = toJson(countExamples(query))
    const examples = await toJson(
        fetchExamples(
            query,
            (idxPage - 1) * EXAMPLE_PAGE_SIZE,
            EXAMPLE_PAGE_SIZE
        )
    )

    return {
        query,
        idxPage,
        examples,
        count
    }
}
