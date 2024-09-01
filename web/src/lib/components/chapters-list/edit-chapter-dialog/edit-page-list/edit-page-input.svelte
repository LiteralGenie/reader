<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import ArrowUturnLeft from '$lib/icons/arrow-uturn-left.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import type { ReadableParam } from '$lib/miscUtils'
    import type { EditChapterFormControls } from '../../edit-chapter-dialog/editChapterContext'

    export let control: ReadableParam<
        EditChapterFormControls['children']['existingPages']['children']
    >[number]
    export let series: string
    export let chapter: string
    export let disabled: boolean = false

    $: ({ value: filenameValue } = control.children.filename)
    $: ({ value: actionValue, setValue: setAction } =
        control.children.action)

    let isEditing = false
    let inputElValue: string | undefined

    $: allowEdit = !disabled && $actionValue?.type !== 'delete'

    function onRenameStart() {
        if ($actionValue?.type === 'rename') {
            inputElValue = $actionValue.filename
        } else {
            inputElValue = $filenameValue
        }

        isEditing = true
    }

    function onRenameEnd() {
        isEditing = false

        let update = (inputElValue ?? '').trim()

        const ext = $filenameValue.split('.').slice(-1)[0]
        if (update && !update.endsWith(ext)) {
            update = update + '.' + ext
        }

        if (update && update !== $filenameValue) {
            setAction({
                type: 'rename',
                filename: update
            })
        } else {
            setAction(null)
        }
    }

    function onDelete() {
        setAction({
            type: 'delete'
        })
    }

    function onRestore() {
        setAction(null)
    }
</script>

<div class="flex {$$restProps['class'] ?? ''} items-center">
    <div class="relative">
        <img
            src="/series/{series}/{chapter}/{$filenameValue}"
            class="w-12 h-16 object-cover"
        />

        <div
            class="absolute top-0 bottom-0 left-0 right-0 bg-background opacity-70"
            class:invisible={$actionValue?.type !== 'delete'}
        ></div>
    </div>

    <button
        on:click={onRenameStart}
        disabled={!allowEdit}
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
        {:else if $actionValue?.type === 'rename'}
            <div
                class="text-sm sm:text-base flex flex-col gap-1 !leading-none"
            >
                <span class="deleted">
                    {$filenameValue}
                </span>
                <span>{$actionValue.filename}</span>
            </div>
        {:else}
            <span
                class="text-sm sm:text-base"
                class:deleted={$actionValue?.type === 'delete'}
            >
                {$filenameValue}
            </span>
        {/if}
    </button>

    <div class="flex">
        {#if $actionValue?.type !== 'delete'}
            <Button
                on:click={onDelete}
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
                on:click={onRestore}
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
</style>
