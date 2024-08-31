<script context="module" lang="ts">
    export interface EditSeriesForm {
        md_id: string
        mu_id: string
        name: string
        cover: File
    }
</script>

<script lang="ts">
    import type { SeriesDto } from '$lib/api/dtos'
    import BasicDialogHeader from '$lib/components/basic-dialog/basic-dialog-header.svelte'
    import BasicDialog from '$lib/components/basic-dialog/basic-dialog.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import { throwOnStatus } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'
    import { createEditSeriesContext } from './editSeriesContext'
    import NameInput from './name-input.svelte'
    import SyncInput from './sync-input.svelte'
    import UploadCoverInput from './upload-cover-input.svelte'

    export let open: boolean
    export let series: SeriesDto

    const { controls, submit } = createEditSeriesContext(series)

    const dispatch = createEventDispatcher()

    async function onSubmit() {
        try {
            const resp = await submit()
            throwOnStatus(resp)

            dispatch('done')
            dispatch('close')
        } catch (e) {
            alert(String(e))
        }
    }
</script>

<BasicDialog
    {open}
    on:close
    class="w-[90vw] max-w-[40em] h-[80vh] m-auto flex flex-col"
>
    <form on:submit|preventDefault={onSubmit} class="contents">
        <div class="flex-1 overflow-auto">
            <BasicDialogHeader label="Editing Knight Run" />

            <div class="flex flex-col pt-0 p-8 gap-4">
                <SyncInput
                    source="MangaDex"
                    href="https://mangadex.org/"
                    placeholder="be06d561-1670-4f1e-a491-0608ba35ce00"
                    name="md_id"
                    control={controls.children.md_id}
                />

                <SyncInput
                    source="MangaUpdates"
                    href="https://www.mangaupdates.com/"
                    placeholder="w1sb5f6"
                    name="mu_id"
                    control={controls.children.mu_id}
                />
            </div>

            <hr class="mx-4" />

            <div class="p-8 flex flex-col gap-4">
                <NameInput control={controls.children.name} />

                <UploadCoverInput
                    control={controls.children.cover}
                    {series}
                />
            </div>
        </div>

        <div class="flex justify-end gap-2 p-4 bg-muted">
            <Button
                type="button"
                variant="outline"
                class="w-24 font-bold"
            >
                Cancel
            </Button>
            <Button type="submit" class="w-24 font-bold">Save</Button>
        </div>
    </form>
</BasicDialog>
