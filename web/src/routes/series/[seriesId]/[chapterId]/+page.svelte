<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrMatch } from '$lib/api/ocr'
    import OcrImage from '$lib/components/OcrImage.svelte'
    import { onMount } from 'svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ pages, ocrData } = data)
    $: ({ seriesId, chapterId } = $page.params)

    onMount(() => {
        const missingOcr = pages.filter(
            (pg) => ocrData[pg.filename] === null
        )

        if (missingOcr.length) {
            const url = new URL(window.location.href)
            url.pathname = `/ocr/${seriesId}/${chapterId}/sse`
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

<div class="text-center w-full flex flex-col items-center">
    <h1>{chapterId}</h1>

    <div class="flex flex-col">
        {#each pages as pg}
            <OcrImage {pg} matches={ocrData[pg.filename] ?? []} />
        {/each}
    </div>
</div>

<style lang="postcss">
</style>
