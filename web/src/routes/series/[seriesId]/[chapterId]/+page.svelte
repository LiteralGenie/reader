<script lang="ts">
    import { page } from '$app/stores'
    import type { PageData } from './$types'

    export let data: PageData
</script>

<div class="flex flex-col">
    <h1>{$page.params.chapterId}</h1>

    {#each data.chapter.pages as pg}
        <img
            src="/series/{$page.params.seriesId}/{$page.params
                .chapterId}/{pg}"
        />
    {/each}
</div>
