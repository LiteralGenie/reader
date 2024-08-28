import { isArray, isObject } from 'radash'
import { FormControl } from './form-control'
import { FormControlArray } from './form-control-array'
import { FormControlRecord } from './form-control-record'
import type { FormControlWrapper, InputParser } from './types'

export const StringParser = {
    fromString: (val: string) => val,
    toString: (val: string) => val
}
export const IntParser = {
    fromString: (val: string) => parseInt(val),
    toString: (val: number) => String(val)
}

// @todo: Not sure why we have to cast this to any
//        maybe related: https://github.com/microsoft/TypeScript/issues/24413
export const BoolParser = {
    fromString: (val: string) => Boolean(val),
    toString: (val: boolean) => String(val)
} as InputParser<any>

export type ValueOf<T> = T[keyof T]

export function createControl<T>(
    initValue: T,
    // @fixme: any
    parser: any,
    onChange: (val: T) => void
): FormControlWrapper<T> {
    if (isArray(initValue)) {
        // @ts-ignore
        return new FormControlArray(onChange, parser, initValue)
    } else if (isObject(initValue)) {
        // @ts-ignore
        return new FormControlRecord(onChange, parser, initValue)
    } else {
        // @ts-ignore
        return new FormControl(onChange, parser)
    }
}

let next_id = 0

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
