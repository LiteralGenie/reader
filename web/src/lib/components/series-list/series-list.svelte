<script lang="ts">
    import type { SeriesDto } from '$lib/api/dtos'
    import Plus from '$lib/icons/plus.svelte'
    import AppHeader from '../app-header/app-header.svelte'
    import Button from '../ui/button/button.svelte'
    import AddSeriesDialog from './add-series-dialog/add-series-dialog.svelte'
    import SeriesRow from './series-row.svelte'

    export let series: SeriesDto[]

    let showAddSeriesDialog = false
</script>

<div class="flex flex-col h-full w-full">
    <AppHeader />

    <div class="flex justify-end p-4 pb-0">
        <Button
            on:click={() => (showAddSeriesDialog = true)}
            class="flex gap-1 px-4 ripple"
        >
            <Plus
                class="size-4 stroke-[3px] stroke-primary-foreground"
            />
            <span class="uppercase font-bold"> Add Series </span>
        </Button>
    </div>

    <div class="list">
        {#each series as s}
            <SeriesRow series={s} />
        {/each}
    </div>
</div>

<AddSeriesDialog
    open={showAddSeriesDialog}
    on:close={() => (showAddSeriesDialog = false)}
/>

<style lang="postcss">
    .list {
        @apply grid items-center justify-center p-4 h-full gap-y-4;
        grid-template-columns: 4em 1fr;
        grid-auto-rows: 4em;
    }
</style>
