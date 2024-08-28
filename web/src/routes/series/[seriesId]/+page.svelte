<script lang="ts">
    import ChaptersPage from '$lib/components/chapters-list/chapters-list.svelte'
    import type { PageData } from './$types'

    export let data: PageData
</script>

<ChaptersPage series={data.series} />
