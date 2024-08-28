<script lang="ts">
    import BasicDialog from '$lib/components/basic-dialog.svelte'
    import Loader from '$lib/components/loader.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import { sleep } from 'radash'
    import { createEventDispatcher } from 'svelte'
    import ImageInput from './image-input.svelte'

    export let open: boolean

    const dispatch = createEventDispatcher()

    let isSubmitting = false

    async function onSubmit(ev: SubmitEvent) {
        isSubmitting = true

        try {
            const data = new FormData(ev.target as HTMLFormElement)
            console.log([...data.entries()])

            await sleep(3000)
        } finally {
            isSubmitting = false
        }
    }
</script>

<BasicDialog
    {open}
    on:close
    preventClose={isSubmitting}
    class="w-[90vw] max-w-[40em] h-max px-6 pb-8 m-auto"
>
    <!-- Title -->
    <div class="pt-5 pb-8 flex items-center">
        <h1 class="text-xl font-bold">Add Chapter</h1>
    </div>

    <form on:submit|preventDefault={onSubmit} class="flex flex-col">
        <div class="flex flex-col gap-2">
            <Label for="name">Chapter Name *</Label>
            <Input
                name="name"
                required
                accept="image/*"
                class="text-xs"
                placeholder="069 - Human Age"
                disabled={isSubmitting}
            />
        </div>

        <ImageInput {isSubmitting} class="py-6" />

        <div class="pt-2 flex flex-col gap-4">
            <Button
                disabled={isSubmitting}
                on:click={() => dispatch('close')}
                variant="secondary">Cancel</Button
            >
            <Button
                disabled={isSubmitting}
                type="submit"
                class="flex gap-1"
            >
                <span>Submit</span>
                {#if isSubmitting}
                    <Loader
                        class="size-3 stroke-primary-foreground text-primary-foreground"
                        showTrack={false}
                    />
                {/if}
            </Button>
        </div>
    </form>
</BasicDialog>
