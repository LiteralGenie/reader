import { objectify } from 'radash'
import {
    derived,
    get,
    type Subscriber,
    type Writable
} from 'svelte/store'
import type {
    FormControl,
    TemplateArray,
    TemplateRecord,
    TemplateScalar,
    TemplateToControlType,
    TemplateToSourceType,
    TemplateType
} from './types'

/**

### Example usage ###

interface Data {
    a: string
    b: {
        c: number
        d: boolean
    }
}

const data = writable({
    a: "",
    b: {
        c: 1,
        d: true
    }
} satisfies Data)

const controls = createFormControlRecord(data, {
    _type: 'record',
    a: { _type: 'scalar' },
    b: {
        _type: 'record',
        children: {
            c: { _type: 'scalar' },
            d: { _type: 'scalar' }
        }
    },
} satisfies TemplateRecord<Data>)

// Reading and updating all Data
controls.value.subscribe(data => console.log(data))     // { a: "lol", b: { c: 1, d: true } }
controls.setValue({ a: "lol", { c: 2, d: true }})       // { a: "lol", b: { c: 2, d: true } }
// (or just call data.subscribe() and data.set() directly)

// Reading and updating Data.b
const controlB = controls.children.b
controlB.value.subscribe(b => ...)                      // { a: "lol", b: { c: 2, d: true } }
controlB.setValue({ c: 3, d: false })                   // { a: "lol", b: { c: 3, d: false } }

// Reading and updating Data.b.c
const controlC = controlB.children.c
controlC.value.subscribe(c => ...)                      // { a: "lol", b: { c: 3, d: false } }
controlC.setValue(4)                                    // { a: "lol", b: { c: 4, d: false } }


### Motivation ###

Given data of an arbitrary shape:

interface Data {
    a: string
    b: {
        c: string
    }
    d: string[]
}

The goal is to define "controls" (a pair of getter / setter functions)
that can be used to read / update (possibly nested) properties of the data.

The key being that each control already knows the path to the property they are updating.
Callers can be ignorant of the data shape.

For example...

parent.svelte
    ```
    <script lang="ts">
        const data = writable({...})
        const controls = createFormControlRecord(data)

        // This parent component will be notified when children modify the data
        controls.value.subcribe(data => console.log(data))
    </script>

    // This ChildInput reads from / writes to data.a
    <ChildInput control={controls.children.a} />

    // This ChildInput reads from / writes to data.b.c
    <ChildInput control={controls.children.b.children.c} />
    ```

child-input.svelte
    ```
    <script lang="ts">
        export let control: FormControl<string>
        let inputEl: HTMLInputElement

        // Update inputEl when control values is updated programmatically (or by another component referencing this control)
        controlC.value.subscribe(c => inputEl?.value = c)

        // Update parent's data store on user input
        // (Note that we didn't need to pass in data as a prop!)
        function onChange() {
            controlC.setValue(parseInt(inputEl.value))
        }
    </script>

    <input bind:this={inputEl} on:change={onChange} />
    ```

This is essentially what the FormControl / FormControlArray / FormControlRecord interfaces are for.
(Controls for arrays and records have an additional "children" property to access sub-controls)



### Implementation ###

Controls expose an interface similar to Writable stores,
with the main difference being that the source of truth usually lives outside of the control.

To be more specific, the "root" control always wraps a Writable store that's stores the entire state.
For reading, sub-controls expose a derived() store (FormControl.value) that retrieves the slice of the state they target
For writing, sub-controls expose a setValue() method that essentially wraps the Writable.update() method of the root control's store

In terms of pseudo-code...
```
    const rootControl = { 
        value: writable({
            a: "",
            b: {
                c: 1,
                d: true 
            }
        })

        setValue: (update: Data) => this.value.set(update)
    }

    const controlC = {
        source: rootControl

        value: derived(this.source, data => data.b.c),

        setValue: (update: Data[b][c]) => this.source.update(data => ({
            ...data,
            b: {
                ...data.b,
                c: update
            }
        }))
    } 
```

This is all implemented via the WritableSlice class and makes use of recursive magic.

-----

But since the shape of our data is a TypeScript interface, it doesn't exist at runtime
and so we wouldn't really know how to instantiate our controls.

This is where the TemplateScalar / TemplateArray / TemplateRecord interfaces come in.
We can define and nest objects that implement these interfaces in order to describe the structure of our data / controls.

This template instance is then fed to createFormControlRecord() to instantiate the root control and sub-controls. 
In the future these templates will probably include things like validation contraints.
 */

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
            (v) => v?.[this.key] as T[keyof T]
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

export function createFormControlArray<T extends TemplateArray<any>>(
    source: Writable<TemplateToSourceType<T>>,
    template: T
): TemplateToControlType<T> {
    return {
        value: source,
        setValue: (update: T) => source.set(update),
        children: derived(source, (xs) => {
            return xs.map((x, idx) => {
                const slice = new WritableSlice(source, idx)
                return createFormControl(slice, template.children)
            })
        })
    }
}

export function createFormControlRecord<
    T extends TemplateRecord<any>
>(
    source: Writable<TemplateToSourceType<T>>,
    template: T
): TemplateToControlType<T> {
    const entries = Object.entries(template).filter(
        ([k, _]) => k !== '_type'
    ) as Array<[string, TemplateType<any>]>

    return {
        value: source,
        setValue: (update) => source.set(update),
        // @ts-ignore
        children: objectify(
            entries,
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
    template: TemplateType<any>
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
