<script lang="ts">
    import { page } from '$app/stores'
    import type { ExampleDto } from '$lib/api/dtos'
    import ArrowRight from '$lib/icons/arrow-right.svelte'

    export let query: string
    export let examples: ExampleDto[]
    export let count: Promise<number>

    let url = new URL($page.url.origin + '/dictionary/examples')
    $: url.searchParams.set('query', query)
</script>

<div>
    <h1>
        <span class="font-bold text-lg">Examples</span>

        {#await count}
            <span>({examples.length})</span>
        {:then c}
            <span>({c})</span>
        {/await}
    </h1>

    {#if examples.length}
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
            <a
                href={url.href}
                class="border-b border-b-pink-700 leading-none pb-0.5 text-pink-700 flex items-center gap-1"
            >
                <span>
                    {#await count}
                        View all examples
                    {:then c}
                        View all {c} examples
                    {/await}
                </span>

                <ArrowRight class="size-3" />
            </a>
        </div>
    {:else}
        <p class="text-muted-foreground pt-1 text-sm">
            No examples found
        </p>
    {/if}
</div>
