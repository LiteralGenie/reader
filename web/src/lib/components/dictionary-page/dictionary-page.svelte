<script lang="ts">
    import type { DefinitionDto, ExampleDto } from '$lib/api/dtos'
    import Definitions from './definitions.svelte'
    import Examples from './examples.svelte'

    export let query: string
    export let definitions: DefinitionDto[]
    export let definitionCount: Promise<number>
    export let examples: ExampleDto[]
    export let exampleCount: Promise<number>
</script>

<div class="flex flex-col gap-16 p-4">
    <Definitions {query} {definitions} count={definitionCount} />

    <Examples {query} {examples} count={exampleCount} />
</div>
