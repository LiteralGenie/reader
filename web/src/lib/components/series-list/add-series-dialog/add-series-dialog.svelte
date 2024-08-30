<script lang="ts">
    import { goto } from '$app/navigation'
    import BasicDialogHeader from '$lib/components/basic-dialog/basic-dialog-header.svelte'
    import BasicDialog from '$lib/components/basic-dialog/basic-dialog.svelte'
    import LabeledDivider from '$lib/components/labeled-divider.svelte'
    import { createEventDispatcher } from 'svelte'
    import ExternalImportForm from './external-import-form.svelte'
    import {
        importMangaDexSeries,
        importMangaUpdatesSeries,
        importManualSeries
    } from './import-handlers'
    import ManualImportForm from './manual-import-form.svelte'

    export let open: boolean

    const dispatch = createEventDispatcher()

    let isSubmitting = false
    let activeForm = ''

    async function onMangaDexImport(id: string) {
        isSubmitting = true
        activeForm = 'mangadex'

        try {
            const filename = await importMangaDexSeries(id)
            goto(`/series/${filename}`)
            dispatch('close')
        } catch (e) {
            alert(String(e))
        } finally {
            isSubmitting = false
            activeForm = ''
        }
    }

    async function onMangaUpdatesImport(id: string) {
        isSubmitting = true
        activeForm = 'mangaupdates'

        try {
            const filename = await importMangaUpdatesSeries(id)
            goto(`/series/${filename}`)
            dispatch('close')
        } catch (e) {
            alert(String(e))
        } finally {
            isSubmitting = false
            activeForm = ''
        }
    }

    async function onManualImport(data: FormData) {
        isSubmitting = true
        activeForm = 'manual'

        try {
            const filename = await importManualSeries(data)
            goto(`/series/${filename}`)
            dispatch('close')
        } catch (e) {
            alert(String(e))
        } finally {
            isSubmitting = false
            activeForm = ''
        }
    }
</script>

<BasicDialog
    {open}
    on:close
    preventClose={isSubmitting}
    class="w-[90vw] max-w-[40em] h-max pb-8 m-auto"
>
    <!-- Title -->
    <BasicDialogHeader label="Add Series" />

    <!-- Import from external source -->
    <div class="px-6 flex flex-col gap-4">
        <ExternalImportForm
            on:submit={(ev) => onMangaDexImport(ev.detail)}
            name="MangaDex"
            href="https://mangadex.org/"
            placeholder="be06d561-1670-4f1e-a491-0608ba35ce00"
            {isSubmitting}
            showSpinner={isSubmitting && activeForm === 'mangadex'}
        />
        <ExternalImportForm
            on:submit={(ev) => onMangaUpdatesImport(ev.detail)}
            name="BakaUpdates"
            href="https://www.mangaupdates.com/"
            placeholder="w1sb5f6"
            {isSubmitting}
            showSpinner={isSubmitting &&
                activeForm === 'mangaupdates'}
        />
    </div>

    <LabeledDivider label="OR" class="px-6 pb-6 pt-6" />

    <!-- Manual -->
    <div class="px-6">
        <ManualImportForm
            on:submit={(ev) => onManualImport(ev.detail)}
            on:close
            {isSubmitting}
            showSpinner={isSubmitting && activeForm === 'manual'}
        />
    </div>
</BasicDialog>
