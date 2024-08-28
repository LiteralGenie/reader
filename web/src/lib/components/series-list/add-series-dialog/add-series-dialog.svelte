<script lang="ts">
    import { goto } from '$app/navigation'
    import BasicDialog from '$lib/components/basic-dialog.svelte'
    import { createEventDispatcher } from 'svelte'
    import ExternalImportForm from './external-import-form.svelte'
    import { importMangadexSeries } from './external-imports'
    import ManualImportForm from './manual-import-form.svelte'

    export let open: boolean

    const dispatch = createEventDispatcher()

    async function onMangaDexImport(id: string) {
        try {
            const filename = await importMangadexSeries(id)
            goto(`/series/${filename}`)
            dispatch('close')
        } catch (e) {
            alert(String(e))
        }
    }
</script>

<BasicDialog
    {open}
    on:close
    class="w-[90vw] max-w-[40em] h-max px-6 pb-8 m-auto"
>
    <!-- Title -->
    <div class="pt-5 pb-8 flex items-center">
        <h1 class="text-xl font-bold">Add Series</h1>
    </div>

    <!-- Import from external source -->
    <div class="flex flex-col gap-4">
        <ExternalImportForm
            on:submit={(ev) => onMangaDexImport(ev.detail)}
            name="MangaDex"
            href="https://mangadex.org/"
            placeholder="be06d561-1670-4f1e-a491-0608ba35ce00"
        />
        <ExternalImportForm
            name="BakaUpdates"
            href="https://www.mangaupdates.com/"
            placeholder="w1sb5f6"
        />
    </div>

    <!-- Divider -->
    <div
        class="flex w-full items-center text-muted-foreground pt-6 pb-4"
    >
        <hr class="flex-grow border-muted-foreground" />
        <span class="px-2 uppercase text-sm">or</span>
        <hr class="flex-grow border-muted-foreground" />
    </div>

    <!-- Manual -->
    <ManualImportForm on:close />
</BasicDialog>
