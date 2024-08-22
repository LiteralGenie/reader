import { env } from '$env/dynamic/private'
import type { DefinitionDto, ExampleDto, JSONResponse } from './dtos'

export async function fetchDefinitions(
    text: string,
    offset: number,
    limit: number
): Promise<JSONResponse<DefinitionDto[]>> {
    // @ts-ignore
    const url = new URL(env.config.apiUrl + `/definitions/${text}`)
    url.searchParams.set('offset', String(offset))
    url.searchParams.set('limit', String(limit))

    return fetch(url)
}

export async function countDefinitions(
    text: string
): Promise<JSONResponse<number>> {
    const url = new URL(
        // @ts-ignore
        env.config.apiUrl + `/definitions/${text}/count`
    )
    return fetch(url)
}

export async function fetchExamples(
    text: string,
    offset: number,
    limit: number
): Promise<JSONResponse<ExampleDto[]>> {
    // @ts-ignore
    const url = new URL(env.config.apiUrl + `/examples/${text}`)
    url.searchParams.set('offset', String(offset))
    url.searchParams.set('limit', String(limit))

    return fetch(url)
}

export async function countExamples(
    text: string
): Promise<JSONResponse<number>> {
    // @ts-ignore
    const url = new URL(env.config.apiUrl + `/examples/${text}/count`)
    return fetch(url)
}
