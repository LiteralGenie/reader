<script lang="ts">
    import type { PageData } from './$types'

    export let data: PageData
</script>

<div class="flex flex-col">
    <h1>{data.series.name}</h1>

    {#each data.series.chapters as ch}
        <a
            class="underline text-blue-600"
            href="/series/{data.series.name}/{ch.name}"
        >
            {ch.name}
        </a>
    {/each}
</div>
