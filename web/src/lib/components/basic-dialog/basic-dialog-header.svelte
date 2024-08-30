<script lang="ts">
    import XIcon from '$lib/icons/x-icon.svelte'
    import { createEventDispatcher } from 'svelte'
    import Button from '../ui/button/button.svelte'

    export let label: string

    const dispatch = createEventDispatcher()
</script>

<div
    class="flex items-center justify-between pl-6 pr-4 py-4 bg-muted mb-6"
>
    <h1 class="text-xl font-bold">{label}</h1>

    <Button
        variant="ghost"
        class="rounded-full p-0 h-max w-max hover:bg-background"
        on:click={() => dispatch('close')}
    >
        <XIcon class="size-10 p-2 stroke-[3px]" />
    </Button>
</div>
