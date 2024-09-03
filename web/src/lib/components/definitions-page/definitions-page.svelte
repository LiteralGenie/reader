<script lang="ts">
    import { page } from '$app/stores'
    import type { DefinitionDto } from '$lib/api/dtos'
    import { EXAMPLE_PAGE_SIZE } from '$lib/constants'
    import ArrowLeft from '$lib/icons/arrow-left.svelte'
    import { newPromiseStore } from '$lib/promiseStore'
    import SourceLink from '../dictionary-page/source-link.svelte'
    import Paginator from '../paginator/paginator.svelte'

    export let query: string
    export let idxPage: number
    export let definitions: DefinitionDto[]
    export let count: Promise<number>

    const countVal = newPromiseStore(count, idxPage)
    $: maxPage = Math.ceil($countVal.data / EXAMPLE_PAGE_SIZE)

    function hrefBuilder(idxPage: number) {
        const url = new URL($page.url)
        url.searchParams.set('page', String(idxPage))
        return url.href
    }
</script>

<div class="p-4 pb-12">
    <a
        href="/dictionary?query={query}"
        class="flex gap-2 items-center border-b border-pink-700 w-max text-pink-700 font-medium"
    >
        <ArrowLeft class="size-3 stroke-1 stroke-pink-700" />
        <span class="text-sm leading-tight">Back to search</span>
    </a>

    <h1 class="pt-4">
        <span class="font-bold text-lg">Definitions for {query}</span>

        {#await count then c}
            <span class="ml-1">({c})</span>
        {/await}
    </h1>

    <div class="flex flex-col gap-4 mt-4 ml-4">
        {#each definitions as def, idx}
            <div class="flex flex-col gap-1.5 leading-tight">
                <div class="flex gap-1 items-center">
                    <h2 class="font-semibold">
                        <a
                            href="/dictionary?query={def.word}"
                            class="underline"
                        >
                            {def.word}
                        </a>
                    </h2>
                    <span class="text-sm">
                        ({def.pos})
                    </span>
                </div>

                <div>{def.definition}</div>

                <div
                    class="text-sm italic text-muted-foreground self-end"
                >
                    <SourceLink source={def.source} />
                </div>
            </div>

            {#if idx != definitions.length - 1}
                <hr />
            {/if}
        {/each}
    </div>

    <div class="flex justify-center pt-8 pb-4">
        <Paginator currentPage={idxPage} {maxPage} {hrefBuilder} />
    </div>
</div>
