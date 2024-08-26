import { max, min } from 'radash'
import type { JSONResponse } from './api/dtos'

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

export function contains<T>(xs: readonly T[], x: any): boolean {
    return !!xs.find((y) => y === x)
}
export function getWindow(): Window | undefined {
    return typeof window === 'undefined' ? undefined : window
}

export function round(x: number, places = 2) {
    const mult = 10 ** places
    return Math.round(x * mult) / mult
}

export const euc = encodeURIComponent
