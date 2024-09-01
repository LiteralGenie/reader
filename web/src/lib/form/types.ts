import type { Readable } from 'svelte/store'

export interface FormControl<T> {
    value: Readable<T>
    setValue: (x: T) => void
}

export interface FormControlArray<T, V extends FormControl<any>>
    extends FormControl<T[]> {
    children: Readable<V[]>
}

export interface FormControlRecord<
    T,
    V extends { [K in keyof T]: FormControl<any> }
> extends FormControl<T> {
    children: V
}

// prettier-ignore
// export type FormControlType<T> =
//     T extends Array<infer V> ? FormControlArray<V> :
//     T extends Primitive ? FormControl<T> :
//     FormControlRecord<T> | FormControl<T>

// ====================================================

export interface TemplateScalar<T> {
    _type: 'scalar'
}

export interface TemplateArray<T extends TemplateType<any>> {
    _type: 'array'
    children: T
}

export type TemplateRecord<
    T extends { [K in keyof T]: TemplateType<any> }
> = { _type: 'record' } & T

export type TemplateType<T> = T extends {
    [K in keyof T]: TemplateType<T[K]>
}
    ? TemplateRecord<T>
    : TemplateScalar<T> | TemplateArray<T>

// ====================================================

export type TemplateToControlType<T extends TemplateType<any>> =
    T extends TemplateScalar<infer V>
        ? FormControl<V>
        : T extends TemplateArray<infer V>
          ? FormControlArray<
                TemplateToSourceType<V>,
                TemplateToControlType<V>
            >
          : T extends TemplateRecord<infer V>
            ? FormControlRecord<
                  {
                      [K in keyof V]: TemplateToSourceType<V[K]>
                  },
                  {
                      [K in keyof V]: TemplateToControlType<V[K]>
                  }
              >
            : never

// prettier-ignore
export type TemplateToSourceType<T extends TemplateType<any>> = 
    T extends TemplateScalar<infer V> ? V :
    T extends TemplateArray<infer V> ? Array<TemplateToSourceType<V>> :
    T extends TemplateRecord<infer V> ? { [K in keyof V]: TemplateToSourceType<V[K]> }
    : never
