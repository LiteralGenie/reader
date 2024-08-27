<script lang="ts">
    import { page } from '$app/stores'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ seriesId } = $page.params)
</script>

<div class="flex flex-col">
    <h1>{seriesId}</h1>

    {#each data.series.chapters as ch}
        <a
            class="underline text-blue-600"
            href="/series/{seriesId}/{ch.filename}"
        >
            {ch.filename}
        </a>
    {/each}
</div>
