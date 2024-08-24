<script lang="ts">
    import type { ChapterDto } from '$lib/api/series'
    import ChevronLeft from '$lib/icons/chevron-left.svelte'
    import ChevronRight from '$lib/icons/chevron-right.svelte'
    import Button from '../ui/button/button.svelte'
    import ChapterSelect from './chapter-select.svelte'

    export let seriesId: string
    export let chapterId: string
    export let chapters: ChapterDto[]
</script>

<div
    class="flex flex-col items-center justify-center gap-1 bg-muted h-full w-full p-4"
>
    <div class="flex w-full gap-2 items-center justify-center">
        <Button
            variant="secondary"
            class="w-[4em] h-[80%] p-0 bg-secondary"
        >
            <ChevronLeft
                class="text-secondary-foreground w-[2.75em] p-3 stroke-[4px] stroke-secondary-foreground"
            />
        </Button>

        <div class="h-full w-full">
            <ChapterSelect {seriesId} {chapters} value={chapterId} />
        </div>

        <Button
            variant="secondary"
            class="w-[4em] h-[80%] p-0 bg-secondary"
        >
            <ChevronRight
                class="text-secondary-foreground w-[2.75em] p-3 stroke-[4px] stroke-secondary-foreground"
            />
        </Button>
    </div>
</div>
