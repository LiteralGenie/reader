<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrPageDto, PageDto } from '$lib/api/dtos'
    import { getReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import OcrBbox from './ocr-bbox.svelte'

    export let pg: PageDto
    export let ocr: OcrPageDto

    const { settings } = getReaderSettingsContext()

    $: ({ seriesId, chapterId } = $page.params)
</script>

<div class="relative">
    <img
        height={pg.height}
        width={pg.width}
        src="/series/{seriesId}/{chapterId}/{pg.filename}"
        class:debug={$settings.debugBboxs}
    />

    {#each Object.values(ocr) as m}
        <OcrBbox {pg} match={m} />
    {/each}
</div>

<style lang="postcss">
    .debug {
        border-color: hsl(var(--primary) / 50%);
        border-bottom-width: 20px;
    }
</style>
