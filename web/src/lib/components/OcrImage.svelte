<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrMatch } from '$lib/api/ocr'
    import type { MatchDto, PageDto } from '$lib/api/series'

    export let pg: PageDto
    export let matches: OcrMatch[]

    $: ({ seriesId, chapterId } = $page.params)

    // Pre-load all chunks
    $: wordChunks = Object.fromEntries(
        matches.map((m) => [m.value, getChunks(m.value)])
    )

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

    async function getChunks(word: string) {
        const url = new URL($page.url)
        url.pathname = `/chunk/${word}`

        const resp = await fetch(url)
        const data = await resp.json()
        return data.map(([part, pos]: [string, string]) => part)
    }
</script>

<div class="relative">
    <img src="/series/{seriesId}/{chapterId}/{pg.filename}" />

    {#each matches as m}
        <div
            class="overlay absolute z-10"
            style={bboxToAbsolutePos(m.bbox)}
            title={m.value}
        >
            <!-- {m.value} -->
        </div>
    {/each}
</div>

<style lang="postcss">
    .overlay {
        /**background-color: rgba(255, 0, 0, 0.5);**/
        border: 4px solid rgba(255, 0, 0, 0.5);
    }
</style>
