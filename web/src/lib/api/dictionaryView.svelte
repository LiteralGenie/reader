<script lang="ts">
    import type { DictionaryContext } from '$lib/dictionaryContext'
    import type { NlpDto } from './nlp'

    export let ctx: DictionaryContext

    $: words = ctx.sentence.split(' ')

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

<div class="flex flex-col h-full w-full text-left p-4">
    <div>
        {ctx.sentence}
    </div>

    <hr class="my-4" />

    <div>
        {#await ctx.nlp then nlp}
            {#each words as word, idx}
                <div class="mb-4">
                    <h1 class="font-bold">[{word}]</h1>
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
