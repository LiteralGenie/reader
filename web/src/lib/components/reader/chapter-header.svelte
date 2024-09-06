<script lang="ts">
    import type { ChapterDto } from '$lib/api/dtos'
    import ChevronLeft from '$lib/icons/chevron-left.svelte'
    import ChevronRight from '$lib/icons/chevron-right.svelte'
    import Button from '../ui/button/button.svelte'
    import ChapterSelect from './chapter-select.svelte'

    export let seriesId: string
    export let chapterId: string
    export let chapters: ChapterDto[]

    $: idxChapter = chapters.findIndex(
        (ch) => ch.filename === chapterId
    )
    $: hrefPrev =
        idxChapter - 1 >= 0
            ? `/series/${seriesId}/${chapters[idxChapter - 1].filename}`
            : ''
    $: hrefNext =
        idxChapter + 1 < chapters.length
            ? `/series/${seriesId}/${chapters[idxChapter + 1].filename}`
            : ''
</script>

<div
    class="flex flex-col items-center justify-center gap-1 bg-muted h-full w-full p-4"
>
    <div class="flex w-full gap-2 items-center justify-center">
        <Button
            variant="link"
            class="chapter-nav ripple {!hrefPrev ? 'disabled' : ''}"
            href={hrefPrev}
        >
            <ChevronLeft class=" w-[2.75em] p-3 stroke-[4px] " />
        </Button>

        <div class="h-full w-full min-w-0">
            <ChapterSelect {seriesId} {chapters} value={chapterId} />
        </div>

        <Button
            variant="link"
            class="chapter-nav ripple {!hrefNext ? 'disabled' : ''}"
            href={hrefNext}
        >
            <ChevronRight class="w-[2.75em] p-3 stroke-[4px]" />
        </Button>
    </div>
</div>

<style lang="postcss">
    :global(.chapter-nav) {
        @apply w-[4em] h-[80%] p-0 bg-secondary text-secondary-foreground stroke-secondary-foreground;
    }
    :global(.chapter-nav:hover) {
        background-color: color-mix(
            in srgb,
            hsl(var(--secondary)),
            hsl(var(--background)) 12%
        );
    }

    :global(.chapter-nav:hover svg) {
        stroke: color-mix(
            in srgb,
            hsl(var(--secondary-foreground)),
            hsl(var(--secondary)) 15%
        );
        color: color-mix(
            in srgb,
            hsl(var(--secondary-foreground)),
            hsl(var(--secondary)) 15%
        );
    }

    :global(.chapter-nav.disabled) {
        pointer-events: none;
        opacity: 30%;
    }
</style>
