<script lang="ts">
    import { SvelteComponent, createEventDispatcher } from 'svelte'
    import CheckboxIcon from './checkbox-icon.svelte'

    export let id: string
    export let label: string
    export let value: boolean | Boolean
    export let disabled = false
    export let disabledValue = false

    export let suffix: typeof SvelteComponent | null = null
    export let suffixOpts: any = null
    export let suffixClass: string = 'h-3 w-3'
    export let prefix: typeof SvelteComponent | null = null
    export let prefixOpts: any = null
    export let prefixClass: string = 'h-3 w-3'

    $: v = disabled ? disabledValue : (value as boolean)

    const dispatch = createEventDispatcher()
</script>

<button
    {disabled}
    on:click={() => dispatch('change', !value)}
    type="button"
    class="cursor-pointer flex items-center gap-2"
>
    <div class="h-5 w-5 flex items-center justify-center">
        <CheckboxIcon checked={v} />
    </div>

    <label
        for={id}
        class="cursor-pointer flex items-center justify-center gap-1"
    >
        {#if prefix}
            <svelte:component
                this={prefix}
                class={prefixClass}
                {...prefixOpts}
            />
        {/if}
        {label}
        {#if suffix}
            <svelte:component
                this={suffix}
                class={suffixClass}
                {...suffixOpts}
            />
        {/if}
    </label>

    <input type="hidden" {id} name={id} {value} />
</button>
