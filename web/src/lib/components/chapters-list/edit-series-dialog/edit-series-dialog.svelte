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
    import Loader from '$lib/components/loader.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import {
        importMangaDexSeries,
        importMangaUpdatesSeries
    } from '$lib/import-handlers'
    import { throwOnStatus } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'
    import { createEditSeriesContext } from './editSeriesContext'
    import NameInput from './name-input.svelte'
    import SyncInput from './sync-input.svelte'
    import UploadCoverInput from './upload-cover-input.svelte'

    export let open: boolean
    export let series: SeriesDto

    let isSubmitting = false
    let isSyncingDex = false
    let isSyncingMu = false
    $: disabled = isSubmitting || isSyncingDex || isSyncingMu

    const { form, controls, hasChanges, submit } =
        createEditSeriesContext(series)

    $: dexHref =
        'https://mangadex.org' +
        ($form.id_dex ? `/title/${$form.id_dex}` : '')
    $: muHref =
        'mangaupdates.com' +
        ($form.id_mu ? `/series/${$form.id_mu}` : '')

    const dispatch = createEventDispatcher()

    async function onSubmit() {
        isSubmitting = true

        try {
            const resp = await submit()
            throwOnStatus(resp)

            dispatch('done')
            dispatch('close')
        } catch (e) {
            alert(String(e))
        } finally {
            isSubmitting = false
        }
    }
</script>

<BasicDialog
    {open}
    on:close
    class="w-[90vw] max-w-[40em] h-[80vh] m-auto flex flex-col"
    preventClose={disabled}
>
    <form on:submit|preventDefault={onSubmit} class="contents">
        <div class="flex-1 overflow-auto">
            <BasicDialogHeader
                label="Editing {series.name || series.filename}"
                hideClose={disabled}
            />

            <div class="flex flex-col pt-0 p-8 gap-4">
                <SyncInput
                    source="MangaDex"
                    href={dexHref}
                    placeholder="be06d561-1670-4f1e-a491-0608ba35ce00"
                    name="md_id"
                    control={controls.children.id_dex}
                    importFn={importMangaDexSeries}
                    {disabled}
                    bind:isSyncing={isSyncingDex}
                />

                <SyncInput
                    source="MangaUpdates"
                    href={muHref}
                    placeholder="w1sb5f6"
                    name="mu_id"
                    control={controls.children.id_mu}
                    importFn={importMangaUpdatesSeries}
                    {disabled}
                    bind:isSyncing={isSyncingMu}
                />
            </div>

            <hr class="mx-4" />

            <div class="p-8 flex flex-col gap-4">
                <NameInput
                    control={controls.children.name}
                    {disabled}
                />

                <UploadCoverInput
                    control={controls.children.cover}
                    {series}
                    {disabled}
                />
            </div>
        </div>

        <div class="footer flex justify-end gap-2 p-4 bg-muted">
            <Button
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
    </form>
</BasicDialog>

<style lang="postcss">
    .footer :global(.cancel-btn:hover) {
        background-color: color-mix(
            in srgb,
            hsl(var(--muted)),
            hsl(var(--background)) 55%
        );
    }
</style>
