<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrMatch } from '$lib/api/ocr'
    import DictionaryView from '$lib/components/dictionary-view/dictionary-view.svelte'
    import OcrImage from '$lib/components/ocr-image.svelte'
    import { setDictionaryContext } from '$lib/dictionaryContext'
    import { stitchBlocks, stitchLines } from '$lib/stitch'
    import { onMount } from 'svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ pages, ocrData } = data)
    $: ({ seriesId, chapterId } = $page.params)

    const {
        value: dictValue,
        setValue: setDictValue,
        mtlPrefetchQueue,
        nlpPrefetchQueue
    } = setDictionaryContext(null)

    onMount(() => {
        // Prefetch stuff
        const texts = pages
            .flatMap((pg) => {
                const matches = ocrData[pg.filename] ?? []
                const lines = stitchLines(matches)
                const blocks = stitchBlocks(lines)
                return blocks
            })
            .map((blk) => blk.value)

        mtlPrefetchQueue.set(texts)
        nlpPrefetchQueue.set(texts)

        // Subscribe to missing ocr data
        const missingOcr = pages.filter(
            (pg) => ocrData[pg.filename] === null
        )

        if (missingOcr.length) {
            const url = new URL(window.location.href)
            url.pathname = `/api/ocr/${seriesId}/${chapterId}/sse`
            for (let pg of missingOcr) {
                url.searchParams.append('pages', pg.filename)
            }

            const evtSource = new EventSource(url)
            evtSource.onmessage = (ev) => {
                if (ev.data === 'close') {
                    evtSource.close()
                    return
                }

                const data: { filename: string; data: OcrMatch[] } =
                    JSON.parse(ev.data)
                ocrData[data.filename] = data.data

                // Add to prefetch queue
                const lines = stitchLines(data.data)
                const blocks = stitchBlocks(lines)
                const texts = blocks.map((blk) => blk.value)

                mtlPrefetchQueue.update((queue) => [
                    ...queue,
                    ...texts
                ])
                nlpPrefetchQueue.update((queue) => [
                    ...queue,
                    ...texts
                ])
            }
        }
    })

    function onEscape(ev: KeyboardEvent) {
        if (ev.key === 'Escape') {
            setDictValue(null)
        }
    }
</script>

<div
    class="text-center w-full flex flex-col items-center h-full"
    tabindex="-1"
    on:keydown={(ev) => onEscape(ev)}
>
    <h1>{chapterId}</h1>

    <div
        class="flex flex-col min-h-0 flex-1 overflow-auto w-full items-center"
        on:click={() => setDictValue(null)}
    >
        {#each pages as pg}
            <OcrImage {pg} matches={ocrData[pg.filename] ?? []} />
        {/each}
    </div>

    {#if $dictValue}
        <div
            class="overflow-auto h-full w-full max-h-[50%] border-t-4 border-gray-600"
        >
            <DictionaryView value={$dictValue} />
        </div>
    {/if}
</div>

<style lang="postcss">
</style>
