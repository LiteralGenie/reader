import type { Readable } from 'svelte/store'

export interface FormControl<T> {
    value: Readable<T>
    setValue: (x: T) => void
}

export interface FormControlArray<T> extends FormControl<T> {
    children: Readable<Array<FormControl<T>>>
}

export interface FormControlRecord<T extends Object>
    extends FormControl<T> {
    children: {
        [K in keyof T]: FormControl<T[K]>
    }
}

export interface TemplateScalar<T> {
    _type: 'scalar'
}

export interface TemplateArray<T> {
    _type: 'array'
    children: TemplateWrapper<T>
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
