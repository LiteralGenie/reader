<script lang="ts">
    import type { SeriesWithChaptersDto } from '$lib/api/dtos'
    import ChevronLeft from '$lib/icons/chevron-left.svelte'
    import Plus from '$lib/icons/plus.svelte'
    import AppHeader from '../app-header.svelte'
    import Button from '../ui/button/button.svelte'
    import ChapterRow from './chapter-row.svelte'

    export let series: SeriesWithChaptersDto
</script>

<div class="flex flex-col">
    <AppHeader />

    <!-- Buttons -->
    <div class="flex justify-between items-center pl-2 pr-4 py-4">
        <!-- Back button -->
        <Button
            variant="ghost"
            href="/series/"
            class="flex gap-1 p-0 items-center pl-2 pr-4"
        >
            <ChevronLeft
                class="size-3 stroke-[4px] stroke-foreground text-foreground"
            />
            <span class="font-bold">Back</span>
        </Button>

        <!-- Add chapter button -->
        <Button class="flex gap-1 px-4 ripple">
            <Plus
                class="size-4 stroke-[3px] stroke-primary-foreground"
            />
            <span class="uppercase font-bold"> Add Chapter </span>
        </Button>
    </div>

    <!-- Info -->
    <div class="flex gap-8 py-4 px-8">
        <!-- Image -->
        <img
            src="/api/cover/{series.filename}/{series.cover}"
            class="object-cover max-w-[40vw] shadow-lg"
        />

        <!-- Info -->
        <div class="flex flex-col justify-center">
            <h1 class="text-xl font-semibold">
                {series.name || series.filename}
            </h1>
        </div>
    </div>

    <!-- Chapter list -->
    <div class="pt-8 px-4">
        <h2 class="pb-2 font-semibold text-muted-foreground">
            Chapters
        </h2>
        {#each series.chapters.toReversed() as chapter}
            <hr />
            <ChapterRow seriesId={series.filename} {chapter} />
        {/each}
        <hr />
    </div>
</div>

<!-- Fading background image -->
<img src="/api/cover/{series.filename}/{series.cover}" class="bg" />

<style lang="postcss">
    .bg {
        position: fixed;
        z-index: -1;
        top: 10%;
        bottom: 100%;
        left: 0;
        right: 0;
        margin: auto;
        object-fit: cover;

        mask-image: linear-gradient(
            to bottom,
            hsla(var(--background) / 10%) 0%,
            hsla(var(--background) / 7.5%) 33%,
            hsla(var(--background) / 0%) 100%
        );
    }
</style>
