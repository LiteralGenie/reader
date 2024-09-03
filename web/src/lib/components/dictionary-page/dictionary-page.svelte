<script lang="ts">
    import type {
        DefinitionDto,
        ExampleDto,
        PartialDefinition
    } from '$lib/api/dtos'
    import AppHeader from '../app-header/app-header.svelte'
    import Definitions from './definitions-preview.svelte'
    import ExamplesPreview from './examples-preview.svelte'
    import PartialDefinitionsPreview from './partial-definitions-preview.svelte'

    export let query: string
    export let definitions: DefinitionDto[]
    export let definitionCount: Promise<number>
    export let partialDefinitions: Record<string, PartialDefinition>
    export let examples: ExampleDto[]
    export let exampleCount: Promise<number>
</script>

<AppHeader />

<div class="flex flex-col gap-8 p-4 pb-16">
    <Definitions {query} {definitions} count={definitionCount} />

    <ExamplesPreview {query} {examples} count={exampleCount} />

    <PartialDefinitionsPreview {query} {partialDefinitions} />
</div>
