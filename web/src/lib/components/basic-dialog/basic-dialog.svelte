<script lang="ts">
    import { createEventDispatcher } from 'svelte'

    export let open = false
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

    function onKeyDown(ev: KeyboardEvent) {
        // This doesn't always work, especially after a form submit
        // Probably a Chrome bug since it works on Firefox
        // Adding a setTimeout() to re-open breaks open / close functionality entirely
        if (ev.key === 'Escape') {
            ev.preventDefault()

            if (preventClose) {
                return
            }

            dispatch('close')
        }
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
<dialog
    bind:this={dialogEl}
    on:click={handleBackdropClick}
    on:close
    on:keydown={(ev) => onKeyDown(ev)}
    class="bg-transparent rounded-lg"
>
    <div
        class="relative bg-popover text-popover-foreground {$$props.class ??
            ''}"
    >
        <slot />
    </div>
</dialog>

<style lang="postcss">
    dialog::backdrop {
        background-color: rgba(0, 0, 0, 69%);
    }
</style>
