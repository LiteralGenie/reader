<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrMatch } from '$lib/api/dtos'
    import type { MatchDto, PageDto } from '$lib/api/series'
    import { getDictionaryContext } from '$lib/dictionaryContext'
    import {
        stitchBlocks,
        StitchedBlock,
        stitchLines
    } from '$lib/stitch'
    import { max, min } from 'radash'

    export let pg: PageDto
    export let matches: OcrMatch[]

    $: ({ seriesId, chapterId } = $page.params)

    $: lines = stitchLines(matches)
    $: blocks = stitchBlocks(lines)

    const ctx = getDictionaryContext()
    $: dictValue = ctx.value

    function bboxToAbsolutePos(bbox: MatchDto['bbox']) {
        const w = pg.width
        const h = pg.height

        let [y1, x1, y2, x2] = bbox
        x1 = max([x1 - 15, 0])!
        y1 = max([y1 - 15, 0])!
        x2 = min([x2 + 15, w])!
        y2 = min([y2 + 15, h])!

        const left = `${(100 * x1) / w}%`
        const right = `${(100 * (w - x2)) / w}%`
        const top = `${(100 * y1) / h}%`
        const bottom = `${(100 * (h - y2)) / h}%`

        return `left: ${left}; right: ${right}; top: ${top}; bottom: ${bottom};`
    }

    function onClick(block: StitchedBlock) {
        ctx.setValue(block.value)
    }
</script>

<div class="relative">
    <img src="/series/{seriesId}/{chapterId}/{pg.filename}" />

    {#each blocks as blk}
        <div
            class="overlay absolute z-10"
            class:active={blk.value === $dictValue?.text}
            style={bboxToAbsolutePos(blk.bbox)}
            title={blk.value}
            on:click|stopPropagation={() => onClick(blk)}
        >
            <!-- {blk.value} -->
        </div>
    {/each}
</div>

<style lang="postcss">
    .overlay {
        /**background-color: rgba(255, 0, 0, 0.5);**/

        &.active {
            border: 6px solid
                color-mix(
                    in srgb,
                    hsl(var(--accent-foreground)),
                    transparent 20%
                );
        }
    }
</style>
