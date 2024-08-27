<script lang="ts">
    import type { SeriesDto } from '$lib/api/dtos'
    import Plus from '$lib/icons/plus.svelte'
    import Button from '../ui/button/button.svelte'
    import SeriesPageHeader from './series-page-header.svelte'
    import SeriesRow from './series-row.svelte'

    export let series: SeriesDto[]
</script>

<div class="flex flex-col h-full w-full">
    <SeriesPageHeader />

    <div class="flex justify-end p-4 pb-0">
        <Button class="flex gap-1 px-8 ripple">
            <Plus
                class="size-4 stroke-[3px] stroke-primary-foreground"
            />
            <span class="uppercase text-md font-bold"> Add </span>
        </Button>
    </div>

    <div class="list">
        {#each series as s}
            <SeriesRow series={s} />
        {/each}
    </div>
</div>

<style lang="postcss">
    .list {
        @apply grid items-center justify-center p-4 h-full gap-y-4;
        grid-template-columns: 4em 1fr;
        grid-auto-rows: 4em;
    }
</style>
