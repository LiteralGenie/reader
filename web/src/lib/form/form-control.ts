import type { FormInput, InputParser } from './types'

type OnChangeHandler<T> = (val: T) => void

export class FormControl<T> {
    inputs: FormInput[] = []
    private subSink: Array<() => void> = []

    constructor(
        public onChange: OnChangeHandler<T>,
        public parser: InputParser<T>
    ) {}

    setValue(val: T) {
        let parsed = this.parser.toString(val)
        this.inputs.forEach((inp) => (inp.value = parsed))
    }

    register(inp: FormInput, initial: string) {
        inp.value = initial
        this.inputs.push(inp)

        const onChange = () => this.publishValue(inp.value, inp)

        inp.addEventListener('change', onChange)
        this.subSink.push(() =>
            inp.removeEventListener('change', onChange)
        )

        // @todo: handle element unmount
    }

    publishValue(val: string, ignore?: FormInput) {
        this.inputs
            .filter((inp) => inp !== ignore)
            .forEach((inp) => (inp.value = val))

        let parsed = this.parser.fromString(val)
        this.onChange(parsed)
    }

    destroy() {
        this.subSink.forEach((unsubscribe) => unsubscribe())
    }
}
