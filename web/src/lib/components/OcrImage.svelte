<script lang="ts">
    import { browser } from '$app/environment'
    import { page } from '$app/stores'
    import { type NlpDto } from '$lib/api/nlp'
    import type { OcrMatch } from '$lib/api/ocr'
    import type { MatchDto, PageDto } from '$lib/api/series'
    import { stitchBlocks, stitchLines } from '$lib/stitch'

    export let pg: PageDto
    export let matches: OcrMatch[]

    const nlpData: Record<string, Promise<NlpDto[][]>> = {}

    $: ({ seriesId, chapterId } = $page.params)

    $: lines = stitchLines(matches)
    $: blocks = stitchBlocks(lines)

    $: {
        if (browser) {
            for (let blk of blocks) {
                if (blk.value in nlpData) {
                    continue
                }

                const url = `/api/nlp/${blk.value}`
                nlpData[blk.value] = fetch(url).then((resp) =>
                    resp.json()
                )
            }
        }
    }

    function bboxToAbsolutePos(bbox: MatchDto['bbox']) {
        const w = pg.width
        const h = pg.height
        const [y1, x1, y2, x2] = bbox

        const left = `${(100 * x1) / w}%`
        const right = `${(100 * (w - x2)) / w}%`
        const top = `${(100 * y1) / h}%`
        const bottom = `${(100 * (h - y2)) / h}%`

        return `left: ${left}; right: ${right}; top: ${top}; bottom: ${bottom};`
    }
</script>

<div class="relative">
    <img src="/series/{seriesId}/{chapterId}/{pg.filename}" />

    {#each blocks as blk}
        <div
            class="overlay absolute z-10"
            style={bboxToAbsolutePos(blk.bbox)}
            title={blk.value}
        >
            <!-- {blk.value} -->
        </div>
    {/each}
</div>

<style lang="postcss">
    .overlay {
        /**background-color: rgba(255, 0, 0, 0.5);**/
        border: 4px solid rgba(255, 0, 0, 0.5);
    }
</style>
