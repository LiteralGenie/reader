<script lang="ts">
    import type {
        ChapterDto,
        SeriesWithChaptersDto
    } from '$lib/api/dtos'
    import ChevronLeft from '$lib/icons/chevron-left.svelte'
    import Cog_6 from '$lib/icons/cog-6.svelte'
    import MangaDex from '$lib/icons/manga-dex.svelte'
    import MangaUpdates from '$lib/icons/manga-updates.svelte'
    import Plus from '$lib/icons/plus.svelte'
    import AppHeader from '../app-header/app-header.svelte'
    import Button from '../ui/button/button.svelte'
    import AddChapterDialog from './add-chapter-dialog/add-chapter-dialog.svelte'
    import ChapterRow from './chapter-row.svelte'
    import EditChapterDialog from './edit-chapter-dialog/edit-chapter-dialog.svelte'
    import EditSeriesDialog from './edit-series-dialog/edit-series-dialog.svelte'

    export let series: SeriesWithChaptersDto

    let showEditSeries = false
    let showAddChapter = false
    let showEditChapter: ChapterDto | null = null

    async function refresh() {
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
                on:click={() => (showEditSeries = true)}
                variant="secondary"
                class="flex gap-2 ripple bg-muted text-foreground"
            >
                <Cog_6 class="size-4" />
                <span class="uppercase font-bold hidden sm:inline">
                    Edit Series
                </span>
            </Button>

            <!-- Add Chapter button -->
            <Button
                on:click={() => (showAddChapter = true)}
                class="flex gap-1 px-4 ripple"
            >
                <Plus
                    class="size-4 stroke-[3px] stroke-primary-foreground"
                />
                <span class="uppercase font-bold hidden sm:inline">
                    Add Chapter
                </span>
            </Button>
        </div>
    </div>

    <!-- Info -->
    <div class="flex gap-8 py-4 px-8">
        {#if series.cover}
            <!-- Image -->
            <img
                src="/api/cover/{series.filename}/{series.cover}"
                class="object-cover w-[40vw] max-w-[20em] shadow-lg"
            />
        {/if}

        <!-- Info -->
        <div class="flex flex-col justify-center">
            <!-- Title -->
            <h1 class="text-2xl lg:text-4xl font-semibold pb-4">
                {series.name || series.filename}
            </h1>

            <!-- External links -->
            <div class="flex gap-2 flex-wrap">
                {#if series.id_mangadex}
                    <a
                        href="https://mangadex.org/title/{series.id_mangadex}"
                        class="pill dex-pill"
                    >
                        <MangaDex class="size-4" />
                        <span class="hidden sm:inline">MangaDex</span>
                    </a>
                {/if}

                {#if series.id_mangaupdates}
                    <a
                        href="https://www.mangaupdates.com/series/{series.id_mangaupdates}"
                        class="pill mu-pill"
                    >
                        <MangaUpdates class="size-4" />
                        <span class="hidden sm:inline"
                            >BakaUpdates</span
                        >
                    </a>
                {/if}
            </div>
        </div>
    </div>

    <!-- Chapter list -->
    <div class="flex flex-col pt-8 px-4">
        <h2 class="pb-2 font-semibold text-muted-foreground">
            Chapters
        </h2>
        {#each series.chapters.toReversed() as chapter}
            <hr />
            <ChapterRow
                on:edit={() => (showEditChapter = chapter)}
                seriesId={series.filename}
                {chapter}
            />
        {/each}
        <hr />

        {#if !series.chapters.length}
            <p
                class="m-auto pt-[5vw] w-full flex justify-center text-muted-foreground"
            >
                No chapters found
            </p>
        {/if}
    </div>
</div>

<!-- Fading background image -->
<img src="/api/cover/{series.filename}/{series.cover}" class="bg" />

<AddChapterDialog
    open={showAddChapter}
    seriesId={series.filename}
    on:close={() => (showAddChapter = false)}
    on:done={refresh}
/>

{#if showEditSeries}
    <EditSeriesDialog
        open={true}
        {series}
        on:close={() => (showEditSeries = false)}
        on:done={refresh}
    />
{/if}

{#if showEditChapter}
    <EditChapterDialog
        open={true}
        series={series.filename}
        chapter={showEditChapter}
        on:close={() => (showEditChapter = null)}
        on:done={refresh}
    />
{/if}

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

    .pill {
        @apply border-2 border-muted-foreground rounded-md py-1 px-4 text-xs flex gap-1 font-bold;

        border-color: color-mix(
            in srgb,
            var(--site-color),
            hsl(var(--background)) 50%
        );
        color: var(--site-color);
    }

    :global(.pill svg) {
        @apply drop-shadow-sm;
    }

    .dex-pill {
        --site-color: #ff6740;
    }

    .mu-pill {
        --site-color: #8a8f96;
    }
</style>
