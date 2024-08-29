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
    <div class="flex flex-col gap-2">
        <Label for="name">Chapter Name *</Label>
        <Input
            name="name"
            required
            accept="image/*"
            class="text-xs"
            placeholder="069 - Human Age"
            {disabled}
        />
    </div>

    <ImageInput isSubmitting={disabled} class="py-6" />

    <div class="pt-2 flex flex-col gap-4">
        <Button
            {disabled}
            on:click={() => dispatch('close')}
            variant="secondary">Cancel</Button
        >
        <Button {disabled} type="submit" class="flex gap-1">
            <span>Submit</span>
            {#if disabled}
                <Loader
                    class="size-3 stroke-primary-foreground text-primary-foreground"
                    showTrack={false}
                />
            {/if}
        </Button>
    </div>
</form>
