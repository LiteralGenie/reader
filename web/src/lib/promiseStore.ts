import { writable, type Readable } from 'svelte/store'

export function newPromiseStore<T>(
    data: Promise<T>,
    init: T
): Readable<T> {
    const store = writable<T>(init)
    data.then((d) => store.set(d))
    return store
}
