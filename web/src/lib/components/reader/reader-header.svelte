<script lang="ts">
    import type { SeriesWithChaptersDto } from '$lib/api/dtos'
    import ArrowLongLeft from '$lib/icons/arrow-long-left.svelte'
    import Cog_6 from '$lib/icons/cog-6.svelte'
    import { euc } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'
    import ThemeToggle from '../theme-toggle.svelte'
    import Button from '../ui/button/button.svelte'

    export let series: SeriesWithChaptersDto

    $: href = `/series/${euc(series.filename)}`

    const dispatch = createEventDispatcher()
</script>

<div class="root w-full min-h-16 flex justify-between items-center">
    <Button
        variant="link"
        {href}
        class="back-link py-0 px-4 h-full hover:no-underline min-w-0 overflow-hidden"
    >
        <div
            class="back-link-text min-w-0 flex gap-2 items-center border-b-2 border-transparent text-foreground stroke-foreground"
        >
            <ArrowLongLeft class="w-6 flex-shrink-0 stroke-2" />

            <span
                class="min-w-0 text-lg text-ellipsis overflow-hidden whitespace-nowrap"
            >
                {series.name || series.filename}
            </span>
        </div>
    </Button>

    <div class="pr-2 flex">
        <ThemeToggle
            variant="ghost"
            class="ripple ripple-invert size-10 p-0 rounded-full mx-1 my-2"
        />

        <Button
            on:click={() => dispatch('settings')}
            variant="ghost"
            class="ripple ripple-invert size-10 p-0 rounded-full mx-1 my-2"
        >
            <Cog_6 class="size-6" />
        </Button>
    </div>
</div>

<style lang="postcss">
    .root {
        background-color: var(--header);
    }

    :global(.back-link:hover .back-link-text),
    :global(.back-link:focus .back-link-text) {
        @apply text-primary stroke-primary;
        border-color: hsla(var(--primary) / 80%) !important;
    }
</style>
