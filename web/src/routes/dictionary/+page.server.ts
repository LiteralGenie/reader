import {
    countDefinitions,
    countExamples,
    fetchDefinitions,
    fetchExamples,
    fetchNlpParts
} from '$lib/api/dictionary'
import type { PartialDefinition } from '$lib/api/dtos'
import { toJson } from '$lib/miscUtils'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ url }) => {
    const query = url.searchParams.get('query') ?? ''

    if (query) {
        const definitionCount = toJson(countDefinitions(query))
        const exampleCount = toJson(countExamples(query))

        const [definitions, partialDefinitions, examples] =
            await Promise.all([
                toJson(fetchDefinitions(query, 0, 3)),
                fetchPartialDefinitions(query),
                toJson(fetchExamples(query, 0, 3))
            ])

        return {
            query,
            definitions,
            definitionCount,
            partialDefinitions,
            examples,
            exampleCount
        }
    } else {
        return {
            query,
            definitions: [],
            definitionCount: Promise.resolve(0),
            partialDefinitions: {},
            examples: [],
            exampleCount: Promise.resolve(0)
        }
    }
}

// @todo: this is eye-watering
async function fetchPartialDefinitions(
    query: string
): Promise<Record<string, PartialDefinition>> {
    const parts = await toJson(fetchNlpParts(query))

    const defs = Object.fromEntries(
        await Promise.all(
            parts
                .flatMap((wordParts) => wordParts)
                .map((pt) =>
                    toJson(fetchDefinitions(pt.text, 0, 3)).then(
                        (definitions) =>
                            [
                                pt.text,
                                {
                                    text: pt.text,
                                    definitions
                                }
                            ] as [string, PartialDefinition]
                    )
                )
        )
    )

    return defs
}
