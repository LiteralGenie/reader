<script lang="ts">
    import { page } from '$app/stores'
    import type { OcrMatchDto } from '$lib/api/dtos'
    import type { PageDto } from '$lib/api/series'
    import { getDictionaryContext } from '$lib/contexts/dictionaryContext'
    import { getReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import { max, min } from 'radash'

    export let pg: PageDto
    export let matches: OcrMatchDto[]

    $: ({ seriesId, chapterId } = $page.params)

    const ctx = getDictionaryContext()
    $: dictValue = ctx.value

    const { settings } = getReaderSettingsContext()

    function bboxToAbsolutePos(bbox: OcrMatchDto['bbox']) {
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

    function onClick(match: OcrMatchDto) {
        ctx.setValue(match.value)
    }
</script>

<div class="relative">
    <img
        height={pg.height}
        width={pg.width}
        src="/series/{seriesId}/{chapterId}/{pg.filename}"
    />

    {#each matches as m}
        <div
            class="absolute z-10 select-none"
            class:active={m.value === $dictValue?.text ||
                $settings.debugBboxs}
            style={bboxToAbsolutePos(m.bbox)}
            title={m.value}
            on:click|stopPropagation={() => onClick(m)}
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
