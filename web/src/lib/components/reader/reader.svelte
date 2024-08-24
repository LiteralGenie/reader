<script lang="ts">
    import type { OcrMatch } from '$lib/api/dtos'
    import type { ChapterDto, PageDto } from '$lib/api/series'
    import DictionaryView from '$lib/components/dictionary-view/dictionary-view.svelte'
    import OcrImage from '$lib/components/ocr-image.svelte'
    import { createDictionaryContext } from '$lib/contexts/dictionaryContext'
    import { createReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import { stitchBlocks, stitchLines } from '$lib/stitch'
    import { onMount } from 'svelte'
    import Resizable from '../resizable.svelte'
    import ChapterHeader from './chapter-header.svelte'
    import ReaderHeader from './reader-header.svelte'
    import ReaderSettingsDialog from './reader-settings-dialog.svelte'

    export let chapters: ChapterDto[]
    export let pages: PageDto[]
    export let ocrData: Record<string, OcrMatch[] | null>
    export let seriesId: string
    export let chapterId: string

    const {
        value: dictValue,
        setValue: setDictValue,
        nlpPrefetchQueue,
        bestDefsPrefetchQueue,
        mtlPrefetchQueue
    } = createDictionaryContext(null)

    createReaderSettingsContext()

    let isResizing = false

    let showSettingsDialog = false

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

        nlpPrefetchQueue.set(texts)
        bestDefsPrefetchQueue.set(texts)
        mtlPrefetchQueue.set(texts)

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

                nlpPrefetchQueue.update((queue) => [
                    ...queue,
                    ...texts
                ])
                bestDefsPrefetchQueue.update((queue) => [
                    ...queue,
                    ...texts
                ])
                mtlPrefetchQueue.update((queue) => [
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
    <div
        class="flex flex-col min-h-0 flex-1 overflow-auto w-full items-center"
        class:overflow-hidden={isResizing}
        on:click={() => setDictValue(null)}
    >
        <ReaderHeader
            {seriesId}
            on:settings={() => (showSettingsDialog = true)}
        />

        <ChapterHeader {seriesId} {chapterId} {chapters} />

        {#each pages as pg}
            <OcrImage {pg} matches={ocrData[pg.filename] ?? []} />
        {/each}
    </div>

    {#if $dictValue}
        <Resizable
            storageKey="dict_view_height"
            on:resizestart={() => (isResizing = true)}
            on:resizeend={() => (isResizing = false)}
        >
            <DictionaryView value={$dictValue} />
        </Resizable>
    {/if}
</div>

<ReaderSettingsDialog
    open={showSettingsDialog}
    on:close={() => (showSettingsDialog = false)}
/>
