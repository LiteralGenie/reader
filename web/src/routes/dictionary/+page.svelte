<script lang="ts">
    import DictionaryPage from '$lib/components/dictionary-page/dictionary-page.svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({
        query,
        definitions,
        definitionCount,
        partialDefinitions,
        examples,
        exampleCount
    } = data)
</script>

<DictionaryPage
    {query}
    {definitions}
    {definitionCount}
    {partialDefinitions}
    {examples}
    {exampleCount}
/>
