<script lang="ts">
    import DefinitionsPage from '$lib/components/definitions-page/definitions-page.svelte'
    import type { PageData } from './$types'

    export let data: PageData
</script>

<DefinitionsPage {...data} />
