import { max, min } from 'radash'
import sanitize from 'sanitize-filename'
import type { Readable } from 'svelte/store'
import type { JSONResponse } from './api/dtos'

export type Primitive = string | number | boolean | null | undefined

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

export async function throwOnStatus(
    resp: Response,
    expected = [200]
) {
    const isError = !expected.includes(resp.status)
    if (isError) {
        let msg = resp.statusText
        console.error(resp)

        try {
            const data = await resp.json()
            if (data?.detail) {
                msg += ' ' + data.detail
            }
            console.error(data)
        } catch (e) {}

        throw new Error(msg)
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

export type ReadableParam<T> = T extends Readable<infer V> ? V : never

// https://stackoverflow.com/questions/57683303/how-can-i-see-the-full-expanded-contract-of-a-typescript-type
export type Expand<T> = T extends infer O
    ? { [K in keyof O]: O[K] }
    : never
export type ExpandRecursively<T> = T extends object
    ? T extends infer O
        ? { [K in keyof O]: ExpandRecursively<O[K]> }
        : never
    : T

let next_id = 1

/**
 * UUIDs aren't available on http. This replacement is only meant for testing.
 */
export function getUuidWithFallback(): string {
    const isSsr = typeof window === 'undefined'
    const isHttp = isSsr || window.crypto.randomUUID === undefined
    const hasUuid = !isHttp

    if (hasUuid) {
        return window.crypto.randomUUID()
    } else {
        console.warn(
            'crypto.randomUUID() not available. Falling back to integer ids.'
        )

        const result = (next_id += 1)
        next_id += 1
        return result.toString()
    }
}
