<script lang="ts">
    import { page } from '$app/stores'
    import OcrImage from '$lib/components/OcrImage.svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ pages, ocrData } = data)
    $: ({ seriesId, chapterId } = $page.params)
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
