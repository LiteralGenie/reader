<script lang="ts">
    import type { ChapterDto } from '$lib/api/dtos'
    import BasicDialogHeader from '$lib/components/basic-dialog/basic-dialog-header.svelte'
    import BasicDialog from '$lib/components/basic-dialog/basic-dialog.svelte'
    import ConfirmDialog from '$lib/components/confirm-dialog.svelte'
    import Loader from '$lib/components/loader.svelte'
    import StringInput from '$lib/components/string-input.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Trash from '$lib/icons/trash.svelte'
    import { throwOnStatus } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'
    import type { DeleteCountDto } from '../edit-series-dialog/edit-series-dialog.svelte'
    import EditPageList from './edit-page-list/edit-page-list.svelte'
    import { createEditChapterContext } from './editChapterContext'

    export let series: string
    export let chapter: ChapterDto
    export let open: boolean

    let isSubmitting = false
    let showDeleteConfirmation = false
    let isDeleting = false

    const { submit, controls, hasChanges, errors } =
        createEditChapterContext(series, chapter)

    const dispatch = createEventDispatcher()

    let deleteCount: DeleteCountDto | null = null

    async function onSave() {
        isSubmitting = true

        try {
            const resp = await submit()
            await throwOnStatus(resp)

            dispatch('done')
            dispatch('close')
        } catch (e) {
            alert(String(e))
        } finally {
            isSubmitting = false
        }
    }

    async function onConfirmDelete() {
        showDeleteConfirmation = true
        deleteCount = null

        try {
            const resp = await fetch(
                `/api/count/${series}/${chapter.filename}`
            )
            await throwOnStatus(resp)

            deleteCount = await resp.json()
        } catch (e) {
            alert(String(e))
        }
    }

    async function onDelete() {
        isDeleting = true

        try {
            const resp = await fetch('/api/chapter', {
                method: 'DELETE',
                body: JSON.stringify({
                    series: series,
                    chapter: chapter.filename
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            throwOnStatus(resp)

            dispatch('done')
            dispatch('close')
        } catch (e) {
            alert(String(e))
        } finally {
            isDeleting = false
        }
    }
</script>

<BasicDialog
    {open}
    on:close
    class="w-[90vw] max-w-[40em] h-[80vh] m-auto flex flex-col"
    preventClose={isSubmitting}
>
    <form on:submit|preventDefault={onSave} class="contents">
        <div class="flex-1 overflow-auto">
            <BasicDialogHeader
                on:close
                label="Editing Chapter {chapter.name ||
                    chapter.filename}"
                hideClose={isSubmitting}
            />

            <StringInput
                label="Chapter Name"
                name="name"
                control={controls.children.name}
                disabled={isSubmitting}
                class="px-4 sm:px-8"
                variant="md"
                required
            />

            <EditPageList
                {series}
                chapter={chapter.filename}
                disabled={isSubmitting}
                class="p-4 pt-8 sm:px-8"
            />
        </div>

        <div class="footer p-4 bg-muted flex justify-between">
            <div>
                <Button
                    on:click={onConfirmDelete}
                    type="button"
                    variant="destructive"
                    class="w-24 font-bold flex items-center gap-1"
                    disabled={isSubmitting}
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
                    disabled={isSubmitting}
                >
                    Cancel
                </Button>
                <Button
                    type="submit"
                    class="w-24 font-bold"
                    disabled={isSubmitting ||
                        !$hasChanges ||
                        !!Object.entries($errors).length}
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

<ConfirmDialog
    open={showDeleteConfirmation}
    on:close={() => (showDeleteConfirmation = false)}
    on:confirm={() => onDelete()}
    disabled={isDeleting}
>
    <div class="text-left pb-4 flex flex-col gap-2">
        <p class="font-bold text-lg pr-8">
            <span> Delete </span>

            <span class="text-primary">
                {chapter.name || chapter.filename}?
            </span>
        </p>

        <!-- {#if deleteCount} -->
        <p>
            This will delete
            <span class="text-primary">
                {deleteCount?.folders ?? '??'}
            </span>
            folders,
            <span class="text-primary">
                {deleteCount?.images ?? '??'}
            </span>
            images, and
            <span class="text-primary">
                {deleteCount?.other ?? '??'}
            </span>
            other files.
        </p>
        <!-- {/if} -->
    </div>
</ConfirmDialog>

<style lang="postcss">
    .footer :global(.cancel-btn:hover) {
        background-color: color-mix(
            in srgb,
            hsl(var(--muted)),
            hsl(var(--background)) 55%
        );
    }
</style>
