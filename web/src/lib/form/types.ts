import type { FormControl } from './form-control'
import type { FormControlArray } from './form-control-array'
import type { FormControlRecord } from './form-control-record'

export interface FormInput {
    value: string
    addEventListener: (
        eventName: 'change',
        caldlback: () => void
    ) => void
    removeEventListener: (
        eventName: 'change',
        callback: () => void
    ) => void
}

export interface ControlLike<T> {
    setValue: (val: T) => void
    destroy: () => void
}

export interface InputParser<T> {
    fromString: (x: string) => T
    toString: (x: T) => string
}

export type Primitive = number | string | boolean | Boolean

/**
 * FormParsers<Primitive> = InputParser<Primitive>
 * FormParsers<Primitive[]> = InputParser<Primitive>
 * FormParsers<T extends Object> = { [k in keyof T]: FormParsers<T> }
 */

export type FormParsers<T> = T extends Primitive
    ? InputParser<T>
    : T extends Array<infer V>
      ? FormParsers<V>
      : {
            [K in keyof T]: FormParsers<T[K]>
        }
/**
 * Wrapper<Primitive> = FormControl<Primitive>
 * Wrapper<Primitive[]> = FormControlArray<Primitive>
 * Wrapper<T extends Object> = { [k in keyof T]: Wrapper<T> }
 */

export type FormControlWrapper<T> = T extends Primitive
    ? FormControl<T>
    : T extends Array<infer V>
      ? FormControlArray<V>
      : T extends Object
        ? FormControlRecord<T>
        : never
