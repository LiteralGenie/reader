import { getContext, setContext } from 'svelte'
import {
    get,
    type Readable,
    type Writable,
    writable
} from 'svelte/store'
import type { MtlDto, NlpDto } from './api/dtos'
import { newPromiseStore } from './promiseStore'

const KEY = 'dictionary'

export interface DictionaryContextValue {
    text: string
    nlp: Promise<NlpDto[][]>
    mtl: Readable<MtlDto | null>
}

export interface DictionaryContext {
    value: Writable<DictionaryContextValue | null>
    mtlPrefetchQueue: Writable<string[]>
    nlpPrefetchQueue: Writable<string[]>
    setValue: (text: string) => void
}

export function setDictionaryContext(
    value: DictionaryContextValue | null
) {
    const ctx = {
        value: writable(value),
        mtlPrefetchQueue: writable<string[]>([]),
        nlpPrefetchQueue: writable<string[]>([]),
        setValue
    }

    setContext<DictionaryContext>(KEY, ctx)

    // Fetch and cache items in prefetch queue one-by-one
    ctx.mtlPrefetchQueue.subscribe(async ([fst, ...rest]) => {
        if (fst) {
            await fetchMtl(fst)
            console.log('Prefetching mtl for', fst)

            const [currFst, ...rest] = get(ctx.mtlPrefetchQueue)
            if (currFst === fst) {
                ctx.mtlPrefetchQueue.set(rest)
            }
        }
    })
    ctx.nlpPrefetchQueue.subscribe(async ([fst, ...rest]) => {
        if (fst) {
            await fetchNlpData(fst)
            console.log('Prefetching nlp for', fst)

            const [currFst, ...rest] = get(ctx.nlpPrefetchQueue)
            if (currFst === fst) {
                ctx.nlpPrefetchQueue.set(rest)
            }
        }
    })

    return ctx

    function setValue(text: string | null) {
        if (text === get(ctx.value)?.text) {
            return
        }

        if (text) {
            ctx.value.set({
                text,
                nlp: fetchNlpData(text),
                mtl: newPromiseStore(fetchMtl(text), null)
            })
        } else {
            ctx.value.set(null)
        }
    }

    async function fetchNlpData(text: string): Promise<NlpDto[][]> {
        const url = `/api/nlp/${text}`
        const resp = await fetch(url)
        return await resp.json()
    }

    async function fetchMtl(text: string): Promise<MtlDto | null> {
        const url = `/api/mtl/${text}`
        const resp = await fetch(url)
        return await resp.json()
    }
}

export function getDictionaryContext() {
    return getContext<DictionaryContext>(KEY)
}
