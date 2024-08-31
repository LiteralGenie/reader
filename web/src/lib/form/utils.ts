import type { Unsubscribe } from '$lib/miscUtils'
import type { SvelteComponent } from 'svelte'
import { get, type Writable } from 'svelte/store'
import type { FormControl } from './types'

type InputEl = SvelteComponent<{
    value?: string
}>

export function syncStringInput(
    el: InputEl | undefined,
    control: FormControl<string>,
    subSink: Writable<Unsubscribe[]>
) {
    // Clear old subs
    for (let unsub of get(subSink)) {
        unsub()
    }
    subSink.set([])

    if (!el) {
        return
    }

    // Create new subs
    subSink.set([
        // Update input on control change
        control.value.subscribe((v) => {
            if (el) {
                el.value = v
            }
        }),
        // Update control on input change
        el.$on('change', () => control.setValue(el.value))
    ])
}
