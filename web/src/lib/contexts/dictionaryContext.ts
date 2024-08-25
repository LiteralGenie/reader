import { getContext, setContext } from 'svelte'
import { get, type Writable, writable } from 'svelte/store'
import type {
    BestDefDto,
    MtlDto,
    NlpDto,
    OcrMatchDto,
    PageDto
} from '../api/dtos'
import { newPromiseStore, type PromiseStore } from '../promiseStore'

const KEY = 'dictionary'

export interface DictionaryContextValue {
    page: PageDto
    match: OcrMatchDto
    nlp: PromiseStore<NlpDto[][], null>
    bestDefs: PromiseStore<BestDefDto | null>
    mtl: PromiseStore<MtlDto | null>
}

export interface DictionaryContext {
    dict: Writable<DictionaryContextValue | null>
    mtlPrefetchQueue: Writable<string[]>
    bestDefsPrefetchQueue: Writable<string[]>
    nlpPrefetchQueue: Writable<string[]>
    setDict: (opts: SetValueArgs | null, forceUpdate: boolean) => void
}

interface SetValueArgs {
    page: PageDto
    match: OcrMatchDto
}

export function createDictionaryContext(
    dict: DictionaryContextValue | null
) {
    const ctx = {
        dict: writable(dict),
        nlpPrefetchQueue: writable<string[]>([]),
        bestDefsPrefetchQueue: writable<string[]>([]),
        mtlPrefetchQueue: writable<string[]>([]),
        setDict
    }

    setContext<DictionaryContext>(KEY, ctx)

    // Fetch and cache items in prefetch queue one-by-one
    ctx.nlpPrefetchQueue.subscribe(async ([fst, ...rest]) => {
        if (fst) {
            await fetchNlpData(fst)
            // console.log('Prefetching nlp for', fst)

            const [currFst, ...rest] = get(ctx.nlpPrefetchQueue)
            if (currFst === fst) {
                ctx.nlpPrefetchQueue.set(rest)
            }
        }
    })
    ctx.bestDefsPrefetchQueue.subscribe(async ([fst, ...rest]) => {
        if (fst) {
            await fetchBestDefs(fst)
            // console.log('Prefetching best defs for', fst)

            const [currFst, ...rest] = get(ctx.bestDefsPrefetchQueue)
            if (currFst === fst) {
                ctx.bestDefsPrefetchQueue.set(rest)
            }
        }
    })
    ctx.mtlPrefetchQueue.subscribe(async ([fst, ...rest]) => {
        if (fst) {
            await fetchMtl(fst)
            // console.log('Prefetching mtl for', fst)

            const [currFst, ...rest] = get(ctx.mtlPrefetchQueue)
            if (currFst === fst) {
                ctx.mtlPrefetchQueue.set(rest)
            }
        }
    })

    return ctx

    function setDict(
        args: SetValueArgs | null,
        forceUpdate: boolean = false
    ) {
        if (
            args?.match.id === get(ctx.dict)?.match.id &&
            forceUpdate === false
        ) {
            return
        }

        if (args) {
            const text = args?.match.value

            // Order of entries determines fetch order
            // Leave it alone!
            ctx.dict.set({
                page: args.page,
                match: args.match,
                nlp: newPromiseStore(fetchNlpData(text), null),
                mtl: newPromiseStore(fetchMtl(text), null),
                bestDefs: newPromiseStore(fetchBestDefs(text), null)
            })
        } else {
            ctx.dict.set(null)
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

    async function fetchBestDefs(
        text: string
    ): Promise<BestDefDto | null> {
        const url = `/api/best_defs/${text}`
        const resp = await fetch(url)
        return await resp.json()
    }
}

export function getDictionaryContext() {
    return getContext<DictionaryContext>(KEY)
}
