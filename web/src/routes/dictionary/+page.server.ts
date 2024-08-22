import { countDefinitions, countExamples } from '$lib/api/dictionary'
import type { DefinitionDto, ExampleDto } from '$lib/api/dtos'
import { toJson } from '$lib/miscUtils'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ url, fetch }) => {
    const query = url.searchParams.get('query') ?? ''
    const offset = url.searchParams.get('offset') ?? '0'
    const limit = url.searchParams.get('limit') ?? '10'

    if (query) {
        const definitionCount = toJson(countDefinitions(query))
        const exampleCount = toJson(countExamples(query))

        const [definitions, examples] = await Promise.all([
            toJson<DefinitionDto[]>(
                fetch(
                    `/api/definitions/${query}?offset=${offset}&limit=${limit}`
                )
            ),
            toJson<ExampleDto[]>(
                fetch(
                    `/api/examples/${query}?offset=${offset}&limit=${limit}`
                )
            )
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
            definitionCount: 0,
            examples: [],
            exampleCount: 0
        }
    }
}
