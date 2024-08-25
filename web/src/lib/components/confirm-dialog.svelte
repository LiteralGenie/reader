<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    import BasicDialog from './basic-dialog.svelte'
    import Button from './ui/button/button.svelte'

    export let open = false

    const dispatch = createEventDispatcher()
</script>

<BasicDialog
    {open}
    on:close
    class="min-h-36 min-w-72 h-max px-6 py-8 m-auto flex flex-col justify-between"
    closeIconSize="hidden"
>
    <slot />

    <div class="flex flex-col justify-end gap-2 items-center">
        <Button
            on:click={() => dispatch('confirm')}
            variant="destructive"
            class="delete-button w-full"
        >
            Delete
        </Button>
        <Button
            variant="outline"
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
