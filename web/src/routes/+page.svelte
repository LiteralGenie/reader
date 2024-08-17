<script lang="ts">
    import type { PageData } from './$types'

    export let data: PageData
</script>

<div class="flex flex-col">
    {#each data.series as s}
        <a class="underline text-blue-600" href="/series/{s.name}">
            {s.name}
        </a>
    {/each}
</div>
