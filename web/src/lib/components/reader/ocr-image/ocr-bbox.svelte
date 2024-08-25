<script lang="ts">
    import type { OcrMatchDto, PageDto } from '$lib/api/dtos'
    import { getDictionaryContext } from '$lib/contexts/dictionaryContext'
    import { getReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import { round } from '$lib/miscUtils'
    import { max, min } from 'radash'

    export let pg: PageDto
    export let match: OcrMatchDto

    const ctx = getDictionaryContext()
    $: dictValue = ctx.dict

    const { settings } = getReaderSettingsContext()

    $: active = match.value === $dictValue?.match.value
    $: visible = active || $settings.debugBboxs

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

    function onClick() {
        ctx.setDict({ page: pg, match })
    }
</script>

<div
    style={bboxToAbsolutePos(match.bbox)}
    class="absolute z-10 select-none"
    class:active
    class:visible
    on:click|stopPropagation={onClick}
>
    {#if $settings.debugBboxs}
        <span
            class="font-bold text-foreground bg-background absolute top-[-20px] left-0"
        >
            {round(match.confidence, 3)}
        </span>
    {/if}

    <!-- Hack to fix blurry images caused by scrollbar on desktop Chrome -->
    <!-- https://issues.chromium.org/issues/361824001 -->
    <div class="blurry-fix"></div>
</div>

<style lang="postcss">
    .visible {
        @apply rounded-md;
        border-style: solid;
        border-width: 6px;
        border-color: hsl(var(--primary) / 33%);

        &.active {
            border-color: hsl(var(--primary) / 69%);
        }
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
