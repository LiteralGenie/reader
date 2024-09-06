<script lang="ts">
    import { page } from '$app/stores'
    import Reader from '$lib/components/reader/reader.svelte'
    import type { PageData } from './$types'

    export let data: PageData
    $: ({ series, pages, ocrData } = data)
    $: ({ chapterId } = $page.params)
</script>

<Reader {series} {chapterId} {pages} {ocrData} />
