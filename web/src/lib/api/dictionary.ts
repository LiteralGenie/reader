import { env } from '$env/dynamic/private'
import { euc } from '$lib/miscUtils'
import type {
    DefinitionDto,
    ExampleDto,
    JSONResponse,
    PartialNlpDto
} from './dtos'

export async function fetchDefinitions(
    text: string,
    offset: number,
    limit: number
): Promise<JSONResponse<DefinitionDto[]>> {
    const url = new URL(
        // @ts-ignore
        env.config.apiUrl + `/definitions/${euc(text)}`
    )
    url.searchParams.set('offset', String(offset))
    url.searchParams.set('limit', String(limit))

    return fetch(url)
}

export async function countDefinitions(
    text: string
): Promise<JSONResponse<number>> {
    const url = new URL(
        // @ts-ignore
        env.config.apiUrl + `/definitions/${euc(text)}/count`
    )
    return fetch(url)
}

export async function fetchExamples(
    text: string,
    offset: number,
    limit: number
): Promise<JSONResponse<ExampleDto[]>> {
    // @ts-ignore
    const url = new URL(env.config.apiUrl + `/examples/${euc(text)}`)
    url.searchParams.set('offset', String(offset))
    url.searchParams.set('limit', String(limit))

    return fetch(url)
}

export async function countExamples(
    text: string
): Promise<JSONResponse<number>> {
    const url = new URL(
        // @ts-ignore
        env.config.apiUrl + `/examples/${euc(text)}/count`
    )
    return fetch(url)
}

export async function fetchNlpParts(
    text: string
): Promise<JSONResponse<PartialNlpDto[][]>> {
    // @ts-ignore
    const url = new URL(env.config.apiUrl + `/nlp_parts/${euc(text)}`)
    return fetch(url)
}
