<script lang="ts">
    import { page } from '$app/stores'
    import type { DefinitionDto } from '$lib/api/dtos'
    import ArrowRight from '$lib/icons/arrow-right.svelte'

    export let query: string
    export let definitions: DefinitionDto[]
    export let count: Promise<number>

    $: url = getUrl($page.url.origin, query)

    function getUrl(origin: string, query: string) {
        const url = new URL(origin + '/dictionary/definitions')
        url.searchParams.set('query', query)
        return url
    }
</script>

<div>
    <h1>
        <span class="font-bold text-lg">Definitions</span>

        {#await count}
            <span>({definitions.length})</span>
        {:then c}
            <span>({c})</span>
        {/await}
    </h1>

    {#if definitions.length}
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
            <a
                href={url.href}
                class="border-b border-b-pink-700 leading-none pb-0.5 text-pink-700 flex items-center gap-1"
            >
                <span>
                    {#await count}
                        View all definitions
                    {:then c}
                        View all {c} definitions
                    {/await}
                </span>

                <ArrowRight class="size-3" />
            </a>
        </div>
    {:else}
        <p class="text-muted-foreground pt-1 text-sm">
            No definitions found
        </p>
    {/if}
</div>
