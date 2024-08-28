<script lang="ts">
    import BasicDialog from '$lib/components/basic-dialog.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import ExternalImportForm from './external-import-form.svelte'

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
    <form class="flex flex-col gap-4">
        <h2 class="font-bold text-lg">Manual Import</h2>

        <div class="flex flex-col gap-2">
            <Label for="email">Series Name *</Label>
            <Input class="text-xs" placeholder="Knight Run" />
        </div>

        <div class="flex flex-col gap-1.5">
            <Label for="email-2">Cover Image (optional)</Label>
            <input type="file" class="text-sm" />
        </div>

        <div class="pt-2 flex flex-col gap-4">
            <Button variant="secondary">Cancel</Button>
            <Button>Submit</Button>
        </div>
    </form>
</BasicDialog>
