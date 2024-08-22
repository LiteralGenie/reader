import { env } from '$env/dynamic/private'
import type { JSONResponse } from './dtos'

export async function countDefinitions(
    text: string
): Promise<JSONResponse<number>> {
    const url = new URL(
        // @ts-ignore
        env.config.apiUrl + `/definitions/${text}/count`
    )
    return fetch(url)
}

export async function countExamples(
    text: string
): Promise<JSONResponse<number>> {
    // @ts-ignore
    const url = new URL(env.config.apiUrl + `/examples/${text}/count`)
    return fetch(url)
}
