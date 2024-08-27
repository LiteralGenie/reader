<script lang="ts">
    import type { ChapterDto } from '$lib/api/dtos'

    export let seriesId: string
    export let chapter: ChapterDto
</script>

<a
    href="/series/{seriesId}/{chapter.filename}"
    class="ripple pl-2 py-4 h-full w-full rounded-r-md flex justify-between items-center"
>
    <span class="flex items-center h-full">
        {chapter.name || chapter.filename}
    </span>

    <div
        class="w-24 flex flex-col text-sm text-muted-foreground leading-tight text-end pr-4"
    >
        <span>100 pages</span>
    </div>
</a>

<style lang="postcss">
    .ripple:hover {
        background-color: color-mix(
            in srgb,
            hsl(var(--background)),
            hsl(var(--foreground)) 10%
        );

        transition: background-color 0.2s;
    }
</style>
