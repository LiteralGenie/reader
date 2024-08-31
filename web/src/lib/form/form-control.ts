import { objectify } from 'radash'
import {
    derived,
    get,
    type Subscriber,
    type Writable
} from 'svelte/store'
import type {
    FormControl,
    FormControlArray,
    FormControlRecord
} from './types'

export interface TemplateScalar<T> {
    _type: 'scalar'
}

export interface TemplateArray<T> {
    _type: 'array'
}

export type TemplateRecord<T> = { _type: 'record' } & {
    [K in keyof T]: TemplateWrapper<T[K]>
}

export type TemplateWrapper<T> =
    T extends Array<infer V>
        ? TemplateArray<V>
        : TemplateRecord<T> | TemplateScalar<T>

export type TemplateType =
    | TemplateScalar<any>
    | TemplateArray<any>
    | TemplateRecord<any>

export class WritableSlice<T> {
    constructor(
        public readonly source: Writable<T> | WritableSlice<any>,
        public readonly key: keyof T
    ) {}

    public set(val: T): void {
        const total = get(this.source)
        total[this.key] = val
        this.source.set(total)
    }

    public update(updater: (val: T[keyof T]) => T[keyof T]): void {
        this.source.update((curr) => {
            curr[this.key] = updater(curr[this.key])
            return curr
        })
    }

    public subscribe(cb: Subscriber<T[keyof T]>): any {
        return derived(
            this.source,
            (v) => v[this.key] as T[keyof T]
        ).subscribe(cb)
    }
}

export function createFormControlPrimitive<T>(
    source: Writable<T>,
    template: TemplateScalar<T>
): FormControl<T> {
    return {
        value: source,
        setValue: (update: T) => source.set(update)
    }
}

export function createFormControlArray<T extends any[]>(
    source: Writable<T>,
    template: TemplateArray<T>
): FormControlArray<T> {
    return {
        value: source,
        setValue: (update: T) => source.set(update),
        children: derived(source, (xs) =>
            xs.map((x) => createFormControl(source, template))
        )
    }
}

export function createFormControlRecord<
    T extends Record<string, any>
>(
    source: Writable<T>,
    template: Omit<TemplateRecord<T>, '_type'>
): FormControlRecord<T> {
    return {
        value: source,
        setValue: (update) => source.set(update),
        // @ts-ignore
        children: objectify(
            Object.entries(template).filter(
                ([k, v]) => k !== '_type'
            ),
            ([k, _]) => k,
            ([k, tmpl]) => {
                const slice = new WritableSlice(source, k)
                return createFormControl(slice, tmpl)
            }
        )
    }
}

export function createFormControl<T>(
    source: Writable<T>,
    template: TemplateType
) {
    if (template._type === 'scalar') {
        return createFormControlPrimitive(source, template)
    } else if (template._type === 'array') {
        return createFormControlArray(source, template)
    } else if (template._type === 'record') {
        return createFormControlRecord(source, template)
    } else {
        throw Error()
    }
}
