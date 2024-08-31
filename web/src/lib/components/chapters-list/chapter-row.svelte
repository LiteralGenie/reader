<script lang="ts">
    import type { ChapterDto } from '$lib/api/dtos'
    import Cog_6 from '$lib/icons/cog-6.svelte'
    import { createEventDispatcher } from 'svelte'
    import Button from '../ui/button/button.svelte'

    export let seriesId: string
    export let chapter: ChapterDto

    const dispatch = createEventDispatcher()
</script>

<div class="flex items-center">
    <a
        href="/series/{seriesId}/{chapter.filename}"
        class="ripple pl-2 pr-4 py-4 h-full w-full rounded-sm flex justify-between items-center gap-4"
    >
        <span class="break-all">
            {chapter.name || chapter.filename}
        </span>

        <div
            class="flex gap-6 items-center text-muted-foreground text-center"
        >
            <span>{chapter.num_pages} pages</span>
        </div>
    </a>

    <hr class="py-3 px-1 border-l border-t-0 border-b-0" />

    <Button
        on:click={() => dispatch('edit')}
        variant="ghost"
        class="px-3 border-muted ripple"
    >
        <Cog_6 class="size-5" />
    </Button>
</div>

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
