import { range, sort, zip } from 'radash'
import type { Readable } from 'svelte/motion'
import { derived, get, writable, type Writable } from 'svelte/store'
import {
    type ControlLike,
    type FormControlWrapper,
    type InputParser
} from './types'
import { createControl, getUuidWithFallback } from './utils'

type OnChangeHandler<T> = (vals: T[]) => void
type Id = string

interface ArrayItem<T> {
    id: Id
    control: FormControlWrapper<T>
    index: number
    value: T
}

export class FormControlArray<T> implements ControlLike<T[]> {
    // @jank: making the form control stuff dependent on svelte stores is kinda lame
    //        its only necessary because this is the only form class where controls can be added / removed and callers need to be notified
    //        but is there at least a way to isolate this notification logic?
    //        like instead of making items a store, can we add a itemsStore prop?
    private items: Writable<Record<Id, ArrayItem<T>>> = writable({})

    constructor(
        public onChange: OnChangeHandler<T>,
        public parser: InputParser<T>,
        initValues: T[]
    ) {
        for (let value of initValues) {
            this._add(value)
        }
    }

    public setValue(vals: T[]) {
        // Make the item count match new number of vals
        const diff = vals.length - this.controls.length
        if (diff > 0) {
            for (let idx of range(
                this.controls.length,
                vals.length - 1
            )) {
                this._add(vals[idx])
            }
        } else if (diff < 0) {
            const toRemove = get(this.itemsSorted).slice(diff)

            for (let it of toRemove) {
                this._remove(it.id)
            }
        }

        // Update item values
        const zipped = zip(get(this.itemsSorted), vals)
        for (let [it, val] of zipped) {
            this.setSingleValue(it.id, val)
        }
    }

    public add(initValue: T) {
        this._add(initValue)
    }

    public destroy() {
        for (let item of Object.values(this.items)) {
            item.control.destroy()
        }
    }

    public get controls(): FormControlWrapper<T>[] {
        return get(this.controlsStore)
    }

    public get controlsStore(): Readable<FormControlWrapper<T>[]> {
        return derived(this.itemsSorted, (current) =>
            current.map(({ control }) => control)
        )
    }

    public get values(): T[] {
        return get(this.itemsSorted).map((it) => it.value)
    }

    private get itemsSorted(): Readable<ArrayItem<T>[]> {
        return derived(this.items, (current) =>
            sort(Object.values(current), (it) => it.index)
        )
    }

    private _add(initValue: T): ArrayItem<T> {
        let n = this.controls.length
        let uuid = getUuidWithFallback()

        let control = createControl(initValue, this.parser, (val) =>
            this.setAndPublishValue(uuid, val)
        )

        this.items.update((current) => ({
            ...current,
            [uuid]: {
                id: uuid,
                control,
                index: n,
                value: initValue
            }
        }))

        return get(this.items)[uuid]
    }

    public _remove(id: Id) {
        let items = get(this.itemsSorted)
        let idx = get(this.items)[id].index

        // Decrement index of all items to the right
        for (let item of items.slice(idx + 1)) {
            item.index += 1
        }

        this.items.update((current) => {
            const update = { ...current }
            delete update[id]
            return update
        })
    }

    private setSingleValue(id: Id, val: T) {
        let item = get(this.items)[id]
        // @ts-ignore
        item.control.setValue(val)
        item.value = val
    }

    private setAndPublishValue(id: Id, val: T) {
        if (!get(this.items)[id]) {
            console.warn(
                'FormArray received update from a deleted FormControl'
            )
            return
        }

        this.setSingleValue(id, val)

        const vals = get(this.itemsSorted).map((it) => it.value)

        this.onChange(vals)
    }
}
