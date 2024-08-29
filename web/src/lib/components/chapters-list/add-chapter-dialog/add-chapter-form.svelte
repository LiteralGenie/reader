<script lang="ts">
    import Loader from '$lib/components/loader.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import { createEventDispatcher } from 'svelte'
    import ImageInput from './image-input.svelte'

    const dispatch = createEventDispatcher()

    export let disabled: boolean
</script>

<form on:submit|preventDefault class="flex flex-col">
    <div class="flex flex-col gap-1.5">
        <Label for="name">Chapter Name *</Label>
        <Input
            name="name"
            required
            accept="image/*"
            class="text-xs"
            placeholder="069 - Human Age"
            {disabled}
        />
        <p class="text-xs text-muted-foreground italic">
            For proper ordering, names should be prefixed with the
            chapter number and zero-padded to a consistent number of
            digits.
        </p>
    </div>

    <hr class="my-6 border-muted-foreground opacity-20" />

    <ImageInput isSubmitting={disabled} />

    <div class="pt-2 flex flex-col gap-4">
        <Button
            {disabled}
            on:click={() => dispatch('close')}
            variant="secondary"
        >
            <span class="font-semibold">Cancel</span>
        </Button>
        <Button {disabled} type="submit" class="flex gap-1">
            <span class="font-semibold">Submit</span>
            {#if disabled}
                <Loader
                    class="size-3 stroke-primary-foreground text-primary-foreground"
                    showTrack={false}
                />
            {/if}
        </Button>
    </div>
</form>
