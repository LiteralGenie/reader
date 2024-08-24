<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrMatch } from '$lib/api/dtos'
    import type { MatchDto, PageDto } from '$lib/api/series'
    import { getDictionaryContext } from '$lib/contexts/dictionaryContext'
    import { getReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
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

    const { settings } = getReaderSettingsContext()

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
    <img
        height={pg.height}
        width={pg.width}
        src="/series/{seriesId}/{chapterId}/{pg.filename}"
    />

    {#each blocks as blk}
        <div
            class="absolute z-10 select-none"
            class:active={blk.value === $dictValue?.text ||
                $settings.debugBboxs}
            style={bboxToAbsolutePos(blk.bbox)}
            title={blk.value}
            on:click|stopPropagation={() => onClick(blk)}
        >
            <!-- Hack to fix blurry images caused by scrollbar on desktop Chrome -->
            <!-- https://issues.chromium.org/issues/361824001 -->
            <div class="blurry-fix"></div>
        </div>
    {/each}
</div>

<style lang="postcss">
    .active {
        @apply rounded-md;
        border: 6px solid hsl(var(--primary) / 69%);
    }

    .blurry-fix {
        position: absolute;
        top: 50%;
        left: 50%;
        height: 1px;
        width: 1px;
        background-color: rgba(0, 0, 0, 1%);
    }
</style>
