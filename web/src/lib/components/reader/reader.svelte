<script lang="ts">
    import { goto } from '$app/navigation'
    import type {
        OcrMatchDto,
        OcrPageDto,
        PageDto,
        SeriesWithChaptersDto
    } from '$lib/api/dtos'
    import DictionaryView from '$lib/components/dictionary-view/dictionary-view.svelte'
    import OcrImage from '$lib/components/reader/ocr-image/ocr-image.svelte'
    import { createDictionaryContext } from '$lib/contexts/dictionaryContext'
    import { createReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import { clone } from 'radash'
    import { onDestroy, onMount } from 'svelte'
    import { writable } from 'svelte/store'
    import Resizable from '../resizable.svelte'
    import Button from '../ui/button/button.svelte'
    import ChapterHeader from './chapter-header.svelte'
    import ReaderHeader from './reader-header.svelte'
    import ReaderSettingsDialog from './reader-settings-dialog.svelte'
    import ReaderStatus from './reader-status.svelte'

    export let series: SeriesWithChaptersDto
    export let chapterId: string
    export let pages: PageDto[]
    export let ocrData: Record<string, OcrPageDto | null>

    const {
        dict,
        setDict,
        nlpPrefetchQueue,
        bestDefsPrefetchQueue,
        mtlPrefetchQueue,
        destroy
    } = createDictionaryContext(null)

    createReaderSettingsContext()

    let isResizing = false

    let showSettingsDialog = false

    $: dataStore = writable(ocrData)

    $: idxChapter = series.chapters.findIndex(
        (ch) => ch.filename === chapterId
    )
    $: idxNext =
        idxChapter + 1 < series.chapters.length
            ? idxChapter + 1
            : null
    $: idxPrev = idxChapter - 1 >= 0 ? idxChapter - 1 : null

    let scrollEl: HTMLElement
    $: chapterId && scrollEl?.scrollTo({ top: 0 })

    onMount(() => {
        // Prefetch stuff
        const texts = pages
            .flatMap((pg) =>
                Object.values(ocrData[pg.filename] ?? {})
            )
            .map((m) => m.value)

        nlpPrefetchQueue.set(texts)
        bestDefsPrefetchQueue.set(texts)
        mtlPrefetchQueue.set(texts)

        // Subscribe to missing ocr data
        const missingOcr = pages.filter(
            (pg) => ocrData[pg.filename] === null
        )

        if (missingOcr.length) {
            const url = new URL(window.location.href)
            url.pathname = `/api/ocr/${series.filename}/${chapterId}/sse`
            for (let pg of missingOcr) {
                url.searchParams.append('pages', pg.filename)
            }

            const evtSource = new EventSource(url)
            evtSource.onmessage = (ev) => {
                if (ev.data === 'close') {
                    evtSource.close()
                    return
                }

                const update: {
                    filename: string
                    data: OcrPageDto
                } = JSON.parse(ev.data)

                dataStore.update((curr) => ({
                    ...curr,
                    [update.filename]: update.data
                }))

                // Add to prefetch queue
                // const texts = Object.values(update.data).map(
                //     (m) => m.value
                // )
                // nlpPrefetchQueue.update((queue) => [
                //     ...queue,
                //     ...texts
                // ])
                // bestDefsPrefetchQueue.update((queue) => [
                //     ...queue,
                //     ...texts
                // ])
                // mtlPrefetchQueue.update((queue) => [
                //     ...queue,
                //     ...texts
                // ])
            }
        }
    })

    function onKeydown(ev: KeyboardEvent) {
        if (ev.key === 'Escape') {
            setDict(null)
        } else if (ev.key === 'ArrowLeft') {
            if (idxPrev !== null) {
                goto(getChapterHref(idxPrev))
            }
        } else if (ev.key === 'ArrowRight') {
            if (idxNext !== null) {
                goto(getChapterHref(idxNext))
            }
        }
    }

    function onDelete({
        detail
    }: CustomEvent<{ page: PageDto; match: OcrMatchDto }>) {
        dataStore.update((curr) => {
            const {
                page: { filename },
                match
            } = detail

            const pg = { ...curr }[filename]!
            delete pg[match.id]

            return {
                ...curr,
                [filename]: pg
            }
        })

        setDict(null)
    }

    function onEdit({
        detail
    }: CustomEvent<{
        page: PageDto
        match: OcrMatchDto
        value: string
    }>) {
        dataStore.update((curr) => {
            const update = clone(curr)

            const {
                page: { filename },
                match,
                value
            } = detail

            update[filename]![match.id].value = value

            return update
        })

        setDict(detail, true)
    }

    function getChapterHref(idx: number) {
        return `/series/${series.filename}/${
            series.chapters[idx].filename
        }`
    }

    onDestroy(() => destroy())
</script>

<div
    class="text-center w-full flex flex-col items-center h-full"
    tabindex="-1"
    on:keydown={(ev) => onKeydown(ev)}
>
    <div
        bind:this={scrollEl}
        class="flex flex-col min-h-0 flex-1 overflow-auto w-full items-center"
        class:overflow-hidden={isResizing}
        on:click={() => setDict(null)}
        autofocus
    >
        <div class="headers w-full flex flex-col">
            <ReaderHeader
                {series}
                on:settings={() => (showSettingsDialog = true)}
            />

            <ChapterHeader
                seriesId={series.filename}
                {chapterId}
                chapters={series.chapters}
            />

            <ReaderStatus data={dataStore} />
        </div>

        {#each pages as pg}
            <OcrImage {pg} ocr={$dataStore[pg.filename] ?? {}} />
        {:else}
            <div
                class="flex flex-1 items-center justify-center pt-24 text-muted-foreground text-lg"
            >
                No pages found.
            </div>
        {/each}

        <div class="flex flex-1 h-full w-full items-end">
            <Button
                variant="link"
                class="ripple w-full p-0 min-h-8 bg-secondary text-secondary-foreground font-bold rounded-none"
                href={idxNext
                    ? getChapterHref(idxNext)
                    : `/series/${series.filename}`}
            >
                {idxNext ? 'Next Chapter' : 'Back to overview'}
            </Button>
        </div>
    </div>

    {#if $dict}
        <Resizable
            storageKey="dict_view_height"
            on:resizestart={() => (isResizing = true)}
            on:resizeend={() => (isResizing = false)}
        >
            <DictionaryView
                dict={$dict}
                on:delete={onDelete}
                on:edit={onEdit}
            />
        </Resizable>
    {/if}
</div>

<ReaderSettingsDialog
    open={showSettingsDialog}
    on:close={() => (showSettingsDialog = false)}
/>

<style lang="postcss">
    .headers {
        position: relative;
        z-index: 20;
        box-shadow: 0px 10px 150px rgba(0, 0, 0, 10%);
    }
</style>
