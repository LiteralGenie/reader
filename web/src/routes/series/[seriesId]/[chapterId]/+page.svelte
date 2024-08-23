<script lang="ts">
    import { page } from '$app/stores'
    import Reader from '$lib/components/reader.svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ pages, ocrData } = data)
    $: ({ seriesId, chapterId } = $page.params)
</script>

<Reader {pages} {ocrData} {seriesId} {chapterId} />
