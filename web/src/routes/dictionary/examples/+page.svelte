<script lang="ts">
    import ExamplesPage from '$lib/components/examples-page/examples-page.svelte'
    import type { PageData } from './$types'

    export let data: PageData
</script>

<ExamplesPage {...data} />
