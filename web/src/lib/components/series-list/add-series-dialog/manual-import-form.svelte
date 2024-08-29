<script lang="ts">
    import Loader from '$lib/components/loader.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import { createEventDispatcher } from 'svelte'

    export let isSubmitting = false
    export let showSpinner = false

    const dispatch = createEventDispatcher()

    async function onSubmit(ev: SubmitEvent) {
        const data = new FormData(ev.target as HTMLFormElement)
        dispatch('submit', data)
    }

    function onCancel() {
        dispatch('close')
    }
</script>

<form on:submit|preventDefault={onSubmit} class="flex flex-col gap-4">
    <h2 class="font-bold text-lg">Manual Import</h2>

    <div class="flex flex-col gap-2">
        <Label for="name">Series Name *</Label>
        <Input
            name="name"
            required
            class="text-xs"
            placeholder="Knight Run"
            disabled={isSubmitting}
        />
    </div>

    <div class="flex flex-col gap-1.5">
        <Label for="cover">Cover Image (optional)</Label>
        <input
            name="cover"
            type="file"
            class="text-sm"
            disabled={isSubmitting}
            accept="image/*"
        />
    </div>

    <div class="pt-2 flex flex-col gap-4">
        <Button
            disabled={isSubmitting}
            on:click={onCancel}
            variant="secondary">Cancel</Button
        >
        <Button
            disabled={isSubmitting}
            type="submit"
            class="flex gap-1"
        >
            <span>Submit</span>
            {#if showSpinner}
                <Loader
                    class="size-1 stroke-primary-foreground text-primary-foreground"
                    showTrack={false}
                />
            {/if}
        </Button>
    </div>
</form>
