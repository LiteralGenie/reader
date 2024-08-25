<script lang="ts">
    import type { BestDefDto, NlpDto } from '$lib/api/dtos'
    import type { DictionaryContextValue } from '$lib/contexts/dictionaryContext'
    import Pencil from '$lib/icons/pencil.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import ConfirmDialog from '../confirm-dialog.svelte'
    import Button from '../ui/button/button.svelte'
    import EditBlock from './edit-block.svelte'

    export let value: DictionaryContextValue

    $: words = value.text.split(' ')
    $: ({ mtl, bestDefs } = value)
    value.nlp.then(console.log)

    let containerEl: HTMLDivElement | undefined
    $: value && containerEl?.scrollTo({ top: 0 })

    let showDeleteConfirmation = false

    let showEdit = false

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

    function onDelete() {
        showDeleteConfirmation = false
        alert('todo')
    }

    function onEdit(ev: CustomEvent<string>) {
        showEdit = false
        alert('edit ' + ev.detail)
    }
</script>

<div
    bind:this={containerEl}
    class="h-fit min-h-full w-full text-left p-4 bg-card m-auto"
>
    <div class="max-w-4xl m-auto flex flex-col">
        {#if showEdit === false}
            <div class="flex flex-col">
                <div class="flex flex-col">
                    <span class="font-bold text-xl">
                        {value.text}
                    </span>

                    {#if $mtl}
                        <span class="italic mt-2"
                            >{$mtl.translation}</span
                        >
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
                        <Pencil class="size-5" />
                    </Button>
                </div>
            </div>
        {:else}
            <EditBlock
                value={value.text}
                on:submit={(ev) => onEdit(ev)}
                on:cancel={() => (showEdit = false)}
            />
        {/if}

        <hr class="mb-6 mt-2" />

        <div>
            {#await value.nlp then nlp}
                {#each words as word, idxWord}
                    {@const wordMtl = $mtl?.words[word]}

                    <div class="mb-4">
                        <div>
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
                        </div>

                        {#each nlp[idxWord] as part, idxPart}
                            <div class="ml-4">
                                <span>{part.text}</span>
                                <span class="text-sm">
                                    {prettyPrintKkma(part.pos)}
                                </span>
                            </div>

                            <ul>
                                {#each pickDefs(nlp, idxWord, idxPart, $bestDefs) as def}
                                    <li class="ml-8">
                                        - {def}
                                    </li>
                                {/each}
                            </ul>
                        {/each}
                    </div>
                {/each}
            {/await}
        </div>
    </div>
</div>

<ConfirmDialog
    open={showDeleteConfirmation}
    on:close={() => (showDeleteConfirmation = false)}
    on:confirm={onDelete}
>
    <div class="text-left pb-4">
        <span class="text-lg"> Delete this section? </span>

        <br />

        <p class="pt-2 italic text-sm leading-snug">
            Note: Adding new sections is not currently possible, so
            this is extra permanent.
        </p>
    </div>
</ConfirmDialog>
