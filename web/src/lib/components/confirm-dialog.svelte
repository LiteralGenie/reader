<script lang="ts">
    import XIcon from '$lib/icons/x-icon.svelte'
    import { createEventDispatcher } from 'svelte'
    import BasicDialog from './basic-dialog/basic-dialog.svelte'
    import Button from './ui/button/button.svelte'

    export let open = false
    export let disabled: boolean = false

    const dispatch = createEventDispatcher()
</script>

<BasicDialog
    {open}
    on:close
    class="min-h-36 min-w-72 h-max px-6 py-7 m-auto flex flex-col justify-between"
    closeIconSize="hidden"
    preventClose={disabled}
>
    {#if !disabled}
        <Button
            variant="ghost"
            class="absolute top-4 right-3 rounded-full p-0 h-max w-max hover:bg-background"
            on:click={() => dispatch('close')}
        >
            <XIcon class="size-12 p-2" />
        </Button>
    {/if}

    <slot />

    <div class="flex flex-col justify-end gap-2 items-center">
        <Button
            on:click={() => dispatch('confirm')}
            {disabled}
            variant="destructive"
            class="delete-button w-full"
        >
            Delete
        </Button>
        <Button
            variant="outline"
            {disabled}
            class="w-full hover:bg-muted hover:text-foreground"
        >
            Cancel
        </Button>
    </div>
</BasicDialog>

<style lang="postcss">
    :global(.delete-button):hover {
        background-color: color-mix(
            in srgb,
            hsl(var(--destructive) / 85%),
            #000 10%
        );
    }
</style>
