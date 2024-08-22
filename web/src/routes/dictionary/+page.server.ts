import {
    countDefinitions,
    countExamples,
    fetchDefinitions,
    fetchExamples
} from '$lib/api/dictionary'
import { toJson } from '$lib/miscUtils'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ url, fetch }) => {
    const query = url.searchParams.get('query') ?? ''

    if (query) {
        const definitionCount = toJson(countDefinitions(query))
        const exampleCount = toJson(countExamples(query))

        const [definitions, examples] = await Promise.all([
            toJson(fetchDefinitions(query, 0, 7)),
            toJson(fetchExamples(query, 0, 7))
        ])

        return {
            query,
            definitions,
            definitionCount,
            examples,
            exampleCount
        }
    } else {
        return {
            query,
            definitions: [],
            definitionCount: Promise.resolve(0),
            examples: [],
            exampleCount: Promise.resolve(0)
        }
    }
}
