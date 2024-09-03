import {
    countDefinitions,
    fetchDefinitions
} from '$lib/api/dictionary'
import { EXAMPLE_PAGE_SIZE } from '$lib/constants'
import { toJson } from '$lib/miscUtils'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ url }) => {
    const query = url.searchParams.get('query') ?? ''
    const idxPage = parseInt(url.searchParams.get('page') ?? '1') ?? 1

    const count = toJson(countDefinitions(query))
    const definitions = await toJson(
        fetchDefinitions(
            query,
            (idxPage - 1) * EXAMPLE_PAGE_SIZE,
            EXAMPLE_PAGE_SIZE
        )
    )

    return {
        query,
        idxPage,
        definitions,
        count
    }
}
