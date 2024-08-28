<script lang="ts">
    import BasicDialog from '$lib/components/basic-dialog.svelte'
    import ExternalImportForm from './external-import-form.svelte'
    import ManualImportForm from './manual-import-form.svelte'

    export let open: boolean
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
            label="Import from MangaDex"
            placeholder="be06d561-1670-4f1e-a491-0608ba35ce00"
        />
        <ExternalImportForm
            label="Import from MangaDex"
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
