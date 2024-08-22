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

        const picks = nlp.defs
            .filter((d) => d.definition.length < 50)
            .slice(0, numPicks)

        for (let d of nlp.defs) {
            if (picks.length >= numPicks) {
                break
            }

            if (picks.find((x) => x.definition === d.definition)) {
                continue
            }

            picks.push(d)
        }

        return picks.map((d) => {
            let text = ''

            if (d.word != nlp.text) {
                text += `(${d.word}) `
            }

            text += d.definition

            return text
        })
    }
</script>

<div
    bind:this={containerEl}
    class="flex flex-col h-full w-full text-left p-4 bg-gray-100 overflow-auto"
>
    <div class="flex flex-col">
        <span class="font-bold">{value.text}</span>

        {#if $mtl}
            <span class="italic mt-2">{$mtl.translation}</span>
        {/if}
    </div>

    <hr class="my-4" />

    <div>
        {#await value.nlp then nlp}
            {#each words as word, idx}
                {@const wordMtl = $mtl?.words[word]}

                <div class="mb-4">
                    <div>
                        <h1>
                            <span class="font-bold">[{word}]</span>

                            {#if wordMtl}
                                <span class="italic">
                                    = {wordMtl}
                                </span>
                            {/if}
                        </h1>
                    </div>

                    {#each nlp[idx] as part}
                        <div class="ml-2">
                            {part.text} ({part.pos})
                        </div>

                        <ul>
                            {#each pickDefs(part) as def}
                                <li class="ml-6">
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
