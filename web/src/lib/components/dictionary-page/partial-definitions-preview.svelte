<script lang="ts">
    import type { PartialDefinition } from '$lib/api/dtos'
    import ArrowRight from '$lib/icons/arrow-right.svelte'

    export let query: string
    export let partialDefinitions: Record<string, PartialDefinition>

    // @todo: this is hacky
    $: defs = Object.values(partialDefinitions).filter(
        ({ text }) => text !== query
    )
</script>

{#if defs.length}
    <div>
        <h1>
            <span class="font-bold text-lg">Similar Words</span>
        </h1>

        <div class="ml-4 pt-3 flex flex-col">
            {#each defs as d, idx}
                <div class="flex flex-col gap-2 leading-none">
                    <div class="flex justify-between">
                        <h2 class="font-bold">
                            {d.text}
                        </h2>

                        <a
                            href="/dictionary?query={d.text}"
                            class="border-b border-b-pink-700 leading-none pb-0.5 text-pink-700 flex items-center gap-1"
                        >
                            <span>View results for {d.text} </span>
                            <ArrowRight class="size-3" />
                        </a>
                    </div>

                    {#if d.definitions.length > 0}
                        <div
                            class="flex flex-col gap-1 ml-4 text-sm mr-8"
                        >
                            {#each d.definitions.slice(0, 3) as def}
                                <div>
                                    <h3 class="font-semibold inline">
                                        {def.word}
                                    </h3>
                                    ({def.pos}) - {def.definition}
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>

                {#if idx !== defs.length - 1}
                    <hr class="my-6" />
                {/if}
            {/each}
        </div>
    </div>
{/if}
