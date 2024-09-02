<script context="module" lang="ts">
    export type PageInputState =
        | { type: 'default' }
        | { type: 'delete' }
        | {
              type: 'rename'

              newFilename: string
          }
</script>

<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import ArrowUturnLeft from '$lib/icons/arrow-uturn-left.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import { createEventDispatcher } from 'svelte'

    export let state: PageInputState
    export let filename: string
    export let src: string
    export let isNew = false

    const dispatch = createEventDispatcher()

    let inputElValue = ''
    let isEditing = false

    function onRenameStart() {
        if (state.type === 'rename') {
            inputElValue = state.newFilename
        } else {
            inputElValue = filename
        }

        isEditing = true
    }

    function onRenameEnd() {
        dispatch('rename', inputElValue.trim())

        isEditing = false
    }
</script>

<div class="flex {$$restProps['class'] ?? ''} items-center">
    <div class="relative">
        <a target="_blank" href={src}>
            <img {src} class="w-12 h-16 object-cover" />
        </a>

        <div
            class="absolute top-0 bottom-0 left-0 right-0 bg-background opacity-70"
            class:invisible={state.type !== 'delete'}
        ></div>
    </div>

    <button
        on:click={onRenameStart}
        disabled={state.type === 'delete'}
        class="flex-1 flex items-center justify-start text-start mx-4"
    >
        {#if isEditing}
            <Input
                autofocus
                bind:value={inputElValue}
                on:blur={onRenameEnd}
                on:keydown={(ev) =>
                    ev.key === 'Enter' ? onRenameEnd() : ''}
            />
        {:else if state.type === 'rename'}
            <div class="flex gap-1 items-center min-w-0">
                <div
                    class="text-sm sm:text-base text-wrap break-all flex flex-col gap-1 !leading-none"
                >
                    <span class="deleted">
                        {filename}
                    </span>
                    <span>{state.newFilename}</span>
                </div>

                {#if isNew}
                    <div class="new-pill">NEW</div>
                {/if}
            </div>
        {:else}
            <div class="flex gap-1 items-center min-w-0">
                <span
                    class="text-sm sm:text-base text-wrap break-all"
                    class:deleted={state.type === 'delete'}
                >
                    {filename}
                </span>

                {#if isNew}
                    <div class="new-pill">NEW</div>
                {/if}
            </div>
        {/if}
    </button>

    <div class="flex">
        {#if state.type !== 'delete'}
            <Button
                on:click={() => dispatch('delete')}
                variant="ghost"
                class="edit-page-btn ripple"
            >
                <Trash />
            </Button>
            <Button
                on:click={onRenameStart}
                variant="ghost"
                class="edit-page-btn ripple"
            >
                <PencilSquare />
            </Button>
        {:else}
            <Button
                on:click={() => dispatch('restore')}
                variant="ghost"
                class="edit-page-btn ripple"
            >
                <ArrowUturnLeft />
            </Button>
        {/if}
    </div>
</div>

<style lang="postcss">
    .deleted {
        @apply line-through text-muted-foreground;
    }

    :global(.edit-page-btn) {
        @apply size-10 sm:size-12 rounded-full p-0;
    }

    :global(.edit-page-btn) svg {
        @apply p-[0.7em] sm:p-[0.9em];
    }

    .new-pill {
        @apply rounded-md border flex items-center px-[6px] h-[18px] font-bold ml-1;

        font-size: 0.6rem;
        margin-top: -1px; /** Fixes weirdly offcenter on Chrome */

        background-color: #a5d6a7;
        color: #388e3c;
        border-color: darkgreen;
    }
</style>
