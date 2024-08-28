<script lang="ts">
    import SeriesPage from '$lib/components/series-list/series-list.svelte'
    import type { PageData } from './$types'

    export let data: PageData
</script>

<SeriesPage series={data.series} />
