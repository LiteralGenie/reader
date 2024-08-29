<script lang="ts">
    import type { SeriesWithChaptersDto } from '$lib/api/dtos'
    import ChevronLeft from '$lib/icons/chevron-left.svelte'
    import Cog_6 from '$lib/icons/cog-6.svelte'
    import Plus from '$lib/icons/plus.svelte'
    import AppHeader from '../app-header.svelte'
    import Button from '../ui/button/button.svelte'
    import AddChapterDialog from './add-chapter-dialog/add-chapter-dialog.svelte'
    import ChapterRow from './chapter-row.svelte'

    export let series: SeriesWithChaptersDto

    let showAddChapter = false

    async function onNewChapter() {
        series = await (
            await fetch(`/api/series/${series.filename}`)
        ).json()
    }
</script>

<div class="flex flex-col h-full">
    <AppHeader />

    <!-- Buttons -->
    <div class="flex justify-between items-center pl-2 pr-4 py-4">
        <!-- Back button -->
        <Button
            variant="ghost"
            href="/series/"
            class="flex gap-1 p-0 items-center pl-2 pr-4 stroke-foreground text-foreground hover:stroke-primary hover:text-primary"
        >
            <ChevronLeft class="size-3 stroke-[4px]" />
            <span class="font-bold">Back</span>
        </Button>

        <div class="flex justify-end gap-4">
            <!-- Edit Series button -->
            <Button
                variant="secondary"
                class="flex gap-2 ripple bg-muted text-foreground"
            >
                <Cog_6 class="size-4" />
                <span class="uppercase font-bold"> Edit </span>
            </Button>

            <!-- Add Chapter button -->
            <Button
                on:click={() => (showAddChapter = true)}
                class="flex gap-1 px-4 ripple"
            >
                <Plus
                    class="size-4 stroke-[3px] stroke-primary-foreground"
                />
                <span class="uppercase font-bold"> Add Chapter </span>
            </Button>
        </div>
    </div>

    <!-- Info -->
    <div class="flex gap-8 py-4 px-8">
        <!-- Image -->
        <img
            src="/api/cover/{series.filename}/{series.cover}"
            class="object-cover w-[40vw] max-w-md shadow-lg"
        />

        <!-- Info -->
        <div class="flex flex-col justify-center">
            <h1 class="text-xl font-semibold">
                {series.name || series.filename}
            </h1>
        </div>
    </div>

    <!-- Chapter list -->
    <div class="pt-8 px-4 h-full">
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

<AddChapterDialog
    open={showAddChapter}
    seriesId={series.filename}
    on:close={() => (showAddChapter = false)}
    on:done={onNewChapter}
/>

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
