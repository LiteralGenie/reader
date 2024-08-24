<script lang="ts">
    import { page } from '$app/stores'
    import Reader from '$lib/components/reader/reader.svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ chapters, pages, ocrData } = data)
    $: ({ seriesId, chapterId } = $page.params)
</script>

<Reader {chapters} {pages} {ocrData} {seriesId} {chapterId} />
