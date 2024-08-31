import { max, min } from 'radash'
import sanitize from 'sanitize-filename'
import type { JSONResponse } from './api/dtos'

export type Unsubscribe = () => void

export function abs(x: number) {
    return x > 0 ? x : -x
}

export async function toJson<T>(
    resp: Promise<JSONResponse<T>>
): Promise<T> {
    return await (await resp).json()
}

export function clamp(x: number, mn: number, mx: number) {
    let clamped = x
    clamped = min([clamped, mx])!
    clamped = max([clamped, mn])!
    return clamped
}

export function getWindow(): Window | undefined {
    return typeof window === 'undefined' ? undefined : window
}

export function round(x: number, places = 2) {
    const mult = 10 ** places
    return Math.round(x * mult) / mult
}

export const euc = encodeURIComponent

export function deepCopy<T>(x: T): T {
    return JSON.parse(JSON.stringify(x))
}

export function throwOnStatus(resp: Response, expected = [200]) {
    const isError = !expected.includes(resp.status)
    if (isError) {
        console.error(resp)
        throw new Error(resp.statusText)
    }

    return resp
}

export function addSuffixUntilUnique(
    existing: string[],
    base: string
) {
    const baseFilename = sanitize(base)
    let nameIdx = 2

    let filename = baseFilename
    while (existing.some((fn) => fn === filename)) {
        filename = `${baseFilename}_${nameIdx}`
        nameIdx += 1
    }

    return filename
}

export function isFileEqual(
    a: File | undefined | null,
    b: File | undefined | null
) {
    const props = ['size', 'name', 'lastModified'] as const

    for (let p of props) {
        if (a?.[p] !== b?.[p]) {
            return false
        }
    }

    // @todo compare file contents

    return true
}
