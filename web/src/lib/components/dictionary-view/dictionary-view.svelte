<script lang="ts">
    import { page } from '$app/stores'
    import type { BestDefDto, NlpDto } from '$lib/api/dtos'
    import { type DictionaryContextValue } from '$lib/contexts/dictionaryContext'
    import ArrowTopRightOnSquare from '$lib/icons/arrow-top-right-on-square.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import { createEventDispatcher } from 'svelte'
    import ConfirmDialog from '../confirm-dialog.svelte'
    import Button from '../ui/button/button.svelte'
    import DictionaryStatus from './dictionary-status.svelte'
    import EditBlock from './edit-block.svelte'

    export let dict: DictionaryContextValue
    $: ({ nlp, bestDefs, mtl } = dict)

    $: words = dict.match.value.split(' ')

    // Scroll to top on content change
    let containerEl: HTMLDivElement | undefined
    $: dict && containerEl?.scrollTo({ top: 0 })

    let showDeleteConfirmation = false

    let showEdit = false

    const dispatch = createEventDispatcher()

    function pickDefs(
        nlp: NlpDto[][],
        idxWord: number,
        idxPart: number,
        bestDefs: BestDefDto | null
    ) {
        const numPicks = 5
        const maxChars = 125

        const data = nlp[idxWord][idxPart]

        // Prioritize LLM-picked defs
        const bestIds = bestDefs?.[idxWord][idxPart] ?? []
        const sorted = [
            ...bestIds.map(
                (id) => data.defs.find((d) => d.id === id)!
            ),
            ...data.defs.filter(
                (d) => !bestIds.find((id) => d.id === id)
            )
        ]

        const picks = sorted.slice(0, numPicks)
        return picks.map((d) => {
            let text = ''

            if (d.word != data.text) {
                text += `(${d.word}) `
            }

            let defn = d.definition
            if (defn.length > maxChars) {
                defn = defn.slice(0, maxChars - 3) + '...'
            }
            text += defn

            return text
        })
    }

    function prettyPrintKkma(kkmaPos: string) {
        if (kkmaPos.startsWith('N')) {
            return '(noun)'
        } else if (['VV', 'VCP', 'VCN'].includes(kkmaPos)) {
            return '(verb)'
        } else if (kkmaPos === 'VA') {
            return '(adj.)'
        } else if (kkmaPos === 'VXV') {
            return '(aux. verb)'
        } else if (kkmaPos === 'VXA') {
            return '(aux. adj.)'
        } else if (['MDN', 'MDT'].includes(kkmaPos)) {
            return '(determiner)'
        } else if (kkmaPos === 'MAG') {
            return '(adverb)'
        } else if (kkmaPos === 'MAC') {
            return '(conjunction)'
        } else if (kkmaPos === 'IC') {
            return '(exclamation)'
        } else if (kkmaPos.startsWith('J')) {
            return '(particle)'
        } else if (kkmaPos.startsWith('E')) {
            return '(verb ending)'
        } else if (kkmaPos === 'XPN') {
            return '(prefix)'
        } else if (kkmaPos === 'XPV') {
            return '(verb prefix)'
        } else if (kkmaPos === 'XSN') {
            return '(suffix)'
        } else if (kkmaPos === 'XSV') {
            return '(verb suffix)'
        } else if (kkmaPos === 'XSA') {
            return '(adj. suffix)'
        } else if (kkmaPos === 'XR') {
            return '(stem)'
        } else if (kkmaPos.startsWith('S')) {
            // punctuation / symbols
            return ''
        } else if (kkmaPos === 'OL') {
            return '(loan word)'
        } else if (kkmaPos === 'ON') {
            // number
            return ''
        } else if (kkmaPos === 'UN') {
            // unknown
            return '(unknown)'
        } else {
            return '(unknown)'
        }
    }

    async function onDelete() {
        const resp = await fetch('/api/ocr/delete', {
            method: 'DELETE',
            body: JSON.stringify({
                series: $page.params.seriesId,
                chapter: $page.params.chapterId,
                page: dict.page.filename,
                block: dict.match.id
            })
        })

        if (resp.status !== 200) {
            console.error(resp)
            alert(`Error: ${resp.statusText}`)

            showDeleteConfirmation = false
            return
        }

        dispatch('delete', { page: dict.page, match: dict.match })
        showDeleteConfirmation = false
    }

    async function onEdit(ev: CustomEvent<string>) {
        const resp = await fetch('/api/ocr/text', {
            method: 'PATCH',
            body: JSON.stringify({
                series: $page.params.seriesId,
                chapter: $page.params.chapterId,
                page: dict.page.filename,
                block: dict.match.id,
                text: ev.detail
            })
        })

        if (resp.status !== 200) {
            console.error(resp)
            alert(`Error: ${resp.statusText}`)

            showEdit = false
            return
        }

        dispatch('edit', {
            page: dict.page,
            match: dict.match,
            value: ev.detail
        })
        showEdit = false
    }
</script>

<div class="h-full" bind:this={containerEl}>
    <DictionaryStatus value={dict} />

    <div class="min-h-full w-full text-left p-4 bg-card m-auto">
        <div class="max-w-4xl m-auto flex flex-col">
            {#if showEdit === false}
                <div class="flex flex-col">
                    <div class="flex flex-col">
                        <span class="font-bold text-xl">
                            {dict.match.value}
                        </span>

                        {#if $mtl.data}
                            <span class="italic mt-2">
                                {$mtl.data.translation}
                            </span>
                        {/if}
                    </div>

                    <div class="flex justify-end pr-2 pt-2">
                        <Button
                            variant="ghost"
                            class="rounded-full p-4 h-max w-max"
                            on:click={() =>
                                (showDeleteConfirmation = true)}
                        >
                            <Trash class="size-5" />
                        </Button>

                        <Button
                            variant="ghost"
                            class="rounded-full p-4 h-max w-max"
                            on:click={() => (showEdit = true)}
                        >
                            <PencilSquare class="size-5" />
                        </Button>
                    </div>
                </div>
            {:else}
                <EditBlock
                    value={dict.match.value}
                    on:submit={(ev) => onEdit(ev)}
                    on:cancel={() => (showEdit = false)}
                />
            {/if}

            <hr class="mb-6 mt-2" />

            <div>
                {#if $nlp.status !== 'pending'}
                    {#each words as word, idxWord}
                        {@const wordMtl = $mtl.data?.words[word]}

                        <div class="mb-4">
                            <div class="flex gap-1 items-center">
                                <h1>
                                    <span
                                        class="font-bold text-lg text-accent-foreground"
                                    >
                                        [{word}]
                                    </span>

                                    {#if wordMtl}
                                        <span> = </span>

                                        <span class="italic">
                                            {wordMtl}
                                        </span>
                                    {/if}
                                </h1>

                                <a
                                    href="/dictionary?query={word}"
                                    target="_blank"
                                    class="ripple rounded-full"
                                >
                                    <ArrowTopRightOnSquare
                                        class="size-6 p-1 text-muted-foreground"
                                    />
                                </a>
                            </div>

                            {#each $nlp.data[idxWord] as part, idxPart}
                                <div
                                    class="flex items-center gap-0.5"
                                >
                                    <div class="ml-4">
                                        <span>{part.text}</span>
                                        <span class="text-sm">
                                            {prettyPrintKkma(
                                                part.pos
                                            )}
                                        </span>
                                    </div>

                                    <a
                                        href="/dictionary?query={part.text}"
                                        target="_blank"
                                        class="ripple rounded-full"
                                    >
                                        <ArrowTopRightOnSquare
                                            class="size-[1.375rem] p-1 text-muted-foreground"
                                        />
                                    </a>
                                </div>

                                <ul>
                                    {#each pickDefs($nlp.data, idxWord, idxPart, $bestDefs.data) as def}
                                        <li class="ml-8">
                                            - {def}
                                        </li>
                                    {/each}
                                </ul>
                            {/each}
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
</div>

<ConfirmDialog
    open={showDeleteConfirmation}
    on:close={() => (showDeleteConfirmation = false)}
    on:confirm={() => onDelete()}
>
    <div class="text-left pb-4 flex flex-col gap-2">
        <span class="text-lg font-bold"> Delete this block? </span>

        <span> {dict.match.value} </span>

        <p class="italic text-sm leading-snug">
            Note: Adding new blocks is currently not possible, so this
            is extra permanent!
        </p>
    </div>
</ConfirmDialog>
