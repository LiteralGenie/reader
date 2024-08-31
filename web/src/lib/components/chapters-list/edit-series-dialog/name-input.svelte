<script lang="ts">
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import type { FormControl } from '$lib/form/types'
    import { syncStringInput } from '$lib/form/utils'
    import type { Unsubscribe } from '$lib/miscUtils'
    import { writable } from 'svelte/store'

    export let control: FormControl<string>
    export let disabled = false

    let inputEl: Input
    const subSink = writable<Unsubscribe[]>([])
    $: syncStringInput(inputEl, control, subSink)
</script>

<div class="flex flex-col gap-1.5">
    <Label for="name">Series Name</Label>
    <Input
        bind:this={inputEl}
        {disabled}
        name="name"
        class="text-xs"
    />
</div>
