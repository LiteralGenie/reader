import { getContext, setContext } from 'svelte'
import { type Writable, writable } from 'svelte/store'
import type { NlpDto } from './api/nlp'

const KEY = 'dictionary'

export interface DictionaryContext {
    sentence: string
    nlp: Promise<NlpDto[][]>
}

export function setDictionaryContext(ctx: DictionaryContext | null) {
    const val = writable(ctx)

    setContext<Writable<DictionaryContext | null>>(KEY, val)

    return val
}

export function getDictionaryContext() {
    return getContext<Writable<DictionaryContext | null>>(KEY)
}
