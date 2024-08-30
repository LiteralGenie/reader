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
