<script lang="ts">
    import { page } from '$app/stores'
    import DictionaryView from '$lib/api/dictionaryView.svelte'
    import type { OcrMatch } from '$lib/api/ocr'
    import OcrImage from '$lib/components/OcrImage.svelte'
    import { setDictionaryContext } from '$lib/dictionaryContext'
    import { onMount } from 'svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ pages, ocrData } = data)
    $: ({ seriesId, chapterId } = $page.params)

    const ctx = setDictionaryContext(null)

    onMount(() => {
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
            }
        }
    })
</script>

<div class="text-center w-full flex flex-col items-center h-full">
    <h1>{chapterId}</h1>

    <div
        class="flex flex-col min-h-0 flex-1 overflow-auto w-full items-center"
        on:click={() => ctx.set(null)}
    >
        {#each pages as pg}
            <OcrImage {pg} matches={ocrData[pg.filename] ?? []} />
        {/each}
    </div>

    {#if $ctx}
        <div
            class="overflow-auto h-full w-full max-h-[50%] border-t-4 border-gray-600"
        >
            <DictionaryView ctx={$ctx} />
        </div>
    {/if}
</div>

<style lang="postcss">
</style>
