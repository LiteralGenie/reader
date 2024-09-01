<script lang="ts">
    import type { ChapterDto } from '$lib/api/dtos'
    import BasicDialogHeader from '$lib/components/basic-dialog/basic-dialog-header.svelte'
    import BasicDialog from '$lib/components/basic-dialog/basic-dialog.svelte'
    import Loader from '$lib/components/loader.svelte'
    import StringInput from '$lib/components/string-input.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import { createEventDispatcher } from 'svelte'
    import EditPageList from '../edit-series-dialog/edit-page-list/edit-page-list.svelte'
    import { createEditChapterContext } from './editChapterContext'

    export let series: string
    export let chapter: ChapterDto
    export let open: boolean
    export let disabled = false

    let isSubmitting = false

    const { controls, hasChanges } = createEditChapterContext(chapter)

    const dispatch = createEventDispatcher()

    function onSave() {}

    function onConfirmDelete() {}
</script>

<BasicDialog
    {open}
    on:close
    class="w-[90vw] max-w-[40em] h-[80vh] m-auto flex flex-col"
    preventClose={disabled}
>
    <form on:submit|preventDefault={onSave} class="contents">
        <div class="flex-1 overflow-auto">
            <BasicDialogHeader
                on:close
                label="Editing Chapter {chapter.name ||
                    chapter.filename}"
                hideClose={disabled}
            />

            <StringInput
                label="Chapter Name"
                name="name"
                control={controls.children.name}
                {disabled}
                class="px-4 sm:px-8"
            />

            <EditPageList
                {series}
                chapter={chapter.filename}
                class="px-4 sm:px-8 pt-4"
            />
        </div>

        <div class="footer p-4 bg-muted flex justify-between">
            <div>
                <Button
                    on:click={onConfirmDelete}
                    type="button"
                    variant="destructive"
                    class="w-24 font-bold flex items-center gap-1"
                    {disabled}
                >
                    <Trash class="size-6" />

                    Delete
                </Button>
            </div>

            <div class="flex justify-end gap-2">
                <Button
                    on:click={() => dispatch('close')}
                    type="button"
                    variant="outline"
                    class="cancel-btn w-24 font-bold"
                    {disabled}
                >
                    Cancel
                </Button>
                <Button
                    type="submit"
                    class="w-24 font-bold"
                    disabled={disabled || !$hasChanges}
                >
                    {#if isSubmitting}
                        <Loader
                            class="h-full w-auto stroke-primary-foreground text-primary-foreground"
                            showTrack={false}
                        />
                    {:else}
                        Save
                    {/if}
                </Button>
            </div>
        </div>
    </form>
</BasicDialog>
