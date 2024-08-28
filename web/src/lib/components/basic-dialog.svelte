<script lang="ts">
    import XIcon from '$lib/icons/x-icon.svelte'
    import { createEventDispatcher } from 'svelte'
    import Button from './ui/button/button.svelte'

    export let open = false
    export let closeIconSize = 'size-12 p-2'
    export let preventClose = false

    let dispatch = createEventDispatcher()

    let dialogEl: HTMLDialogElement
    $: open ? dialogEl?.showModal() : dialogEl?.close()

    function handleBackdropClick(ev: MouseEvent) {
        if (preventClose) {
            return
        }

        // This will only trigger on backdrop clicks, not dialog content clicks
        // Because in the latter case, the event target will be one of the inner elements
        if (ev.target === dialogEl) {
            dispatch('close')
        }
    }

    function handleCloseButtonClick() {
        if (preventClose) {
            return
        }

        dispatch('close')
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<dialog
    bind:this={dialogEl}
    on:click={handleBackdropClick}
    on:close
    class="bg-transparent"
>
    <div
        class="relative rounded-md bg-popover text-popover-foreground {$$props.class ??
            ''}"
    >
        {#if !preventClose}
            <Button
                variant="ghost"
                class="absolute top-3 right-3 rounded-full p-0 h-max w-max"
                on:click={handleCloseButtonClick}
            >
                <XIcon class={closeIconSize} />
            </Button>
        {/if}

        <slot />
    </div>
</dialog>

<style lang="postcss">
    dialog::backdrop {
        background-color: rgba(0, 0, 0, 69%);
    }
</style>
