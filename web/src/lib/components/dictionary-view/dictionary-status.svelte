<script lang="ts" context="module">
    const STATUS_CHECK_DELAY = 500
</script>

<script lang="ts">
    import type { BestDefDto, MtlDto, NlpDto } from '$lib/api/dtos'

    import type { DictionaryContextValue } from '$lib/contexts/dictionaryContext'
    import type { PromiseStoreValue } from '$lib/promiseStore'
    import Loader from '../loader.svelte'

    export let value: DictionaryContextValue
    $: ({ nlp, bestDefs, mtl } = value)

    let status = ''
    $: updateStatus($nlp, $mtl, $bestDefs)
    $: setTimeout(
        () => updateStatus($nlp, $mtl, $bestDefs),
        STATUS_CHECK_DELAY
    )

    function updateStatus(
        nlp: PromiseStoreValue<NlpDto[][] | null>,
        mtl: PromiseStoreValue<MtlDto | null>,
        bestDefs: PromiseStoreValue<BestDefDto | null>
    ) {
        const isPending = (p: PromiseStoreValue) => {
            const pending = p.status === 'pending'
            const elapsed =
                Date.now() - p.initTime > STATUS_CHECK_DELAY * 0.9
            return pending && elapsed
        }

        if (isPending(nlp)) {
            status = 'Loading dictionary data...'
        } else if (isPending(mtl)) {
            status = 'Loading machine translations...'
        } else if (isPending(bestDefs)) {
            status = 'Sorting definitions...'
        } else {
            status = ''
        }
    }
</script>

{#if status}
    <div class="w-full bg-muted">
        <div
            class="px-4 max-w-4xl flex items-center justify-start m-auto w-full py-2 text-sm text-muted-foreground"
        >
            <Loader class="size-3 mr-1 stroke-primary fill-primary" />
            <span> {status} </span>
        </div>
    </div>
{/if}
