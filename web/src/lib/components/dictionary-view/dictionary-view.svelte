<script lang="ts">
    import type { NlpDto } from '$lib/api/dtos'
    import type { DictionaryContextValue } from '$lib/dictionaryContext'

    export let value: DictionaryContextValue

    $: words = value.text.split(' ')
    $: ({ mtl } = value)

    let containerEl: HTMLDivElement | undefined
    $: value && containerEl?.scrollTo({ top: 0 })

    function pickDefs(nlp: NlpDto) {
        const numPicks = 5
        const maxChars = 125

        const picks = nlp.defs.slice(0, numPicks)

        return picks.map((d) => {
            let text = ''

            if (d.word != nlp.text) {
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
</script>

<div
    bind:this={containerEl}
    class="flex flex-col h-full w-full text-left p-4 bg-card overflow-auto"
>
    <div class="flex flex-col">
        <span class="font-bold text-xl">
            {value.text}
        </span>

        {#if $mtl}
            <span class="italic mt-2">{$mtl.translation}</span>
        {/if}
    </div>

    <hr class="my-6" />

    <div>
        {#await value.nlp then nlp}
            {#each words as word, idx}
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

                    {#each nlp[idx] as part}
                        <div class="ml-4">
                            <span>{part.text}</span>
                            <span class="text-sm">
                                {prettyPrintKkma(part.pos)}
                            </span>
                        </div>

                        <ul>
                            {#each pickDefs(part) as def}
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
