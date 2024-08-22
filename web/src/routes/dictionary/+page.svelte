<script lang="ts">
    import type { PageData } from './$types'

    export let data: PageData

    const { query, definitionCount, exampleCount } = data
    console.log(data)
</script>

<div class="flex flex-col gap-16">
    <div>Definitions</div>

    <div>Examples</div>
</div>
