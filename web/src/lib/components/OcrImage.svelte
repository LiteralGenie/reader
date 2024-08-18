<script lang="ts">
    import { page } from '$app/stores'
    import type { MatchDto, PageDto } from '$lib/api/series'

    export let pg: PageDto

    $: ({ seriesId, chapterId } = $page.params)

    let imgEl: HTMLImageElement | undefined

    function bboxToAbsolutePos(
        bbox: MatchDto['bbox'],
        imgEl: HTMLImageElement | undefined
    ) {
        const w = imgEl?.naturalWidth ?? 1
        const h = imgEl?.naturalHeight ?? 1
        const [y1, x1, y2, x2] = bbox

        const left = `${(100 * x1) / w}%`
        const right = `${(100 * (w - x2)) / w}%`
        const top = `${(100 * y1) / h}%`
        const bottom = `${(100 * (h - y2)) / h}%`

        return `left: ${left}; right: ${right}; top: ${top}; bottom: ${bottom};`
    }
</script>

<div class="relative">
    <img
        bind:this={imgEl}
        src="/series/{seriesId}/{chapterId}/{pg.filename}"
    />

    {#each pg.matches as m}
        <div
            class="overlay absolute z-10"
            style={bboxToAbsolutePos(m.bbox, imgEl)}
            title={m.value}
        >
            {m.value}
        </div>
    {/each}
</div>

<style lang="postcss">
    .overlay {
        background-color: rgba(255, 0, 0, 0.5);
    }
</style>
