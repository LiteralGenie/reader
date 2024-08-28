import {
    type ControlLike,
    type FormControlWrapper,
    type FormParsers
} from './types'
import { createControl, type ValueOf } from './utils'

type OnChangeHandler<T> = (val: T) => void

type IControls<T> = {
    [K in keyof T]: FormControlWrapper<T[K]>
}

export class FormControlRecord<T extends Object>
    implements ControlLike<T>
{
    controls: IControls<T>

    constructor(
        public onChange: OnChangeHandler<T>,
        public parsers: FormParsers<T>,
        public value: T
    ) {
        // @ts-ignore
        const controls: IControls<T> = {}

        for (let [k, v] of Object.entries(value)) {
            let key = k as keyof T

            // @fixme: ignores
            // @ts-ignore
            const parser = parsers[key]

            // @ts-ignore
            controls[key] = createControl(v, parser, (update) =>
                this.setAndPublishValue(key, update)
            )
        }
        this.controls = controls
    }

    public setValue(x: T) {
        for (let [key, val] of Object.entries(x)) {
            let k = key as keyof T
            let v = val as ValueOf<T>
            // @fixme: ignores
            // @ts-ignore
            this.controls[k].setValue(v)
        }

        this.value = x
    }

    public destroy() {
        for (let control of Object.values(this.controls)) {
            control.destroy()
        }
    }

    private setAndPublishValue(key: keyof T, val: ValueOf<T>) {
        this.value[key] = val
        this.onChange(this.value)
    }
}
