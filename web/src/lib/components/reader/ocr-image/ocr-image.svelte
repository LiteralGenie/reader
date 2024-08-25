<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrPageDto, PageDto } from '$lib/api/dtos'
    import OcrBbox from './ocr-bbox.svelte'

    export let pg: PageDto
    export let ocr: OcrPageDto

    $: ({ seriesId, chapterId } = $page.params)
</script>

<div class="relative">
    <img
        height={pg.height}
        width={pg.width}
        src="/series/{seriesId}/{chapterId}/{pg.filename}"
    />

    {#each Object.values(ocr) as m}
        <OcrBbox {pg} match={m} />
    {/each}
</div>
