<script lang="ts">
    import { page } from '$app/stores'
    import type { DefinitionDto } from '$lib/api/dtos'

    export let query: string
    export let definitions: DefinitionDto[]
    export let count: Promise<number>

    let url = new URL($page.url.origin + '/dictionary/definitions')
    $: url.searchParams.set('query', query)
</script>

<div>
    <h1>
        <span class="font-bold text-lg">Definitions</span>

        {#await count then c}
            <span>({c})</span>
        {/await}
    </h1>

    <div class="ml-4 pt-2 flex flex-col gap-2 leading-tight">
        {#each definitions as d, idx}
            <div class="flex flex-col gap-1">
                <h2>
                    <span class="font-bold">{d.word}</span>

                    {#if d.pos}
                        <span>({d.pos})</span>
                    {/if}
                </h2>

                <div>{d.definition}</div>
            </div>

            {#if idx != definitions.length - 1}
                <hr />
            {/if}
        {/each}
    </div>

    <div class="flex justify-end pt-6">
        <a href={url.href} class="underline text-pink-700">
            {#await count}
                View all definitions ->
            {:then c}
                View all {c} definitions ->
            {/await}
        </a>
    </div>
</div>
