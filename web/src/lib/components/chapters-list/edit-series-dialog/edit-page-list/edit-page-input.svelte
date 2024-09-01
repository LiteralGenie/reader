<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import ArrowUturnLeft from '$lib/icons/arrow-uturn-left.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import { createEventDispatcher } from 'svelte'
    import type { EditChapterForm } from '../../edit-chapter-dialog/editChapterContext'

    export let page: EditChapterForm['existingPages'][number]
    export let series: string
    export let chapter: string
    export let disabled: boolean = false

    const dispatch = createEventDispatcher()

    let isEditing = false
    let inputElValue: string | undefined

    $: allowEdit = !disabled && page?.action?.type !== 'delete'

    function onRename() {
        console.log('inputElValue', inputElValue)
        isEditing = false
    }
</script>

<div class="h-full flex {$$restProps['class'] ?? ''} items-center">
    <img
        src="/series/{series}/{chapter}/{page.filename}"
        class="w-12 h-16 object-cover"
    />

    <button
        on:click={() => (isEditing = true)}
        disabled={!allowEdit}
        class="flex-1 h-full flex items-center justify-start text-start"
    >
        {#if isEditing}
            <Input
                autofocus
                bind:value={inputElValue}
                on:blur={() => onRename()}
                on:keydown={(ev) =>
                    ev.key === 'Enter' ? onRename() : ''}
            />
        {:else if page.action?.type === 'rename'}
            <div
                class="pl-4 pr-4 text-sm sm:text-base flex flex-col gap-1 !leading-none"
            >
                <span class="deleted">
                    {page.filename}
                </span>
                <span>{page.action.filename}</span>
            </div>
        {:else}
            <span
                class="pl-4 pr-4 text-sm sm:text-base"
                class:deleted={page.action?.type === 'delete'}
            >
                {page.filename}
            </span>
        {/if}
    </button>

    <div class="flex">
        {#if page.action?.type !== 'delete'}
            <Button variant="ghost" class="edit-page-btn">
                <Trash />
            </Button>
            <Button variant="ghost" class="edit-page-btn">
                <PencilSquare />
            </Button>
        {:else}
            <Button variant="ghost" class="edit-page-btn">
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
</style>
