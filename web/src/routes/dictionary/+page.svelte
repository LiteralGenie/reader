<script lang="ts">
    import DictionaryPage from '$lib/components/dictionary-page/dictionary-page.svelte'
    import type { PageData } from './$types'

    export let data: PageData
    const {
        query,
        definitions,
        definitionCount,
        examples,
        exampleCount
    } = data
</script>

<DictionaryPage
    {query}
    {definitions}
    {definitionCount}
    {examples}
    {exampleCount}
/>
