<script lang="ts">
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import type { FormControl } from '$lib/form/types'
    import { syncStringInput } from '$lib/form/utils'
    import type { Unsubscribe } from '$lib/miscUtils'
    import { writable } from 'svelte/store'

    export let label: string
    export let name: string
    export let control: FormControl<string>
    export let disabled = false
    export let variant: 'sm' | 'md' = 'sm'
    export let required = false

    $: labelTextSize = {
        sm: 'text-sm',
        md: 'text-base'
    }[variant]
    $: inputTextSize = {
        sm: 'text-xs',
        md: 'text-sm'
    }[variant]

    let inputEl: Input
    const subSink = writable<Unsubscribe[]>([])
    $: syncStringInput(inputEl, control, subSink)
</script>

<div class="flex flex-col gap-1.5 {$$restProps['class'] ?? ''}">
    <Label for={name} class={labelTextSize}>{label}</Label>
    <Input
        bind:this={inputEl}
        {disabled}
        {name}
        class="text-xs {inputTextSize}"
        {required}
    />
</div>
