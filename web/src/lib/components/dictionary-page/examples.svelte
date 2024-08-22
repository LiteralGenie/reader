<script lang="ts">
    import { page } from '$app/stores'
    import type { ExampleDto } from '$lib/api/dtos'

    export let query: string
    export let examples: ExampleDto[]
    export let count: Promise<number>

    let url = new URL($page.url.origin + '/dictionary/examples')
    $: url.searchParams.set('query', query)
</script>

<div>
    <h1>
        <span class="font-bold text-lg">Examples</span>

        {#await count then c}
            <span>({c})</span>
        {/await}
    </h1>

    <div class="flex flex-col gap-4 mt-4 ml-4">
        {#each examples as ex, idx}
            <div class="flex flex-col gap-1 leading-tight">
                <div>{ex.korean}</div>
                <div class="italic">{ex.english}</div>
            </div>

            {#if idx != examples.length - 1}
                <hr />
            {/if}
        {/each}
    </div>

    <div class="flex justify-end pt-6">
        <a href={url.href} class="underline text-pink-700">
            {#await count}
                View all examples ->
            {:then c}
                View all {c} examples ->
            {/await}
        </a>
    </div>
</div>
