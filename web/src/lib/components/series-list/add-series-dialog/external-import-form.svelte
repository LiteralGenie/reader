<script lang="ts">
    import Loader from '$lib/components/loader.svelte'
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import ArrowRight from '$lib/icons/arrow-right.svelte'
    import { createEventDispatcher } from 'svelte'

    export let name: string
    export let href: string
    export let placeholder: string
    export let isSubmitting = false
    export let showSpinner = false

    const dispatch = createEventDispatcher()

    function onSubmit(ev: SubmitEvent) {
        const data = new FormData(ev.target as HTMLFormElement)
        dispatch('submit', data.get('external-id')!)
    }
</script>

<form on:submit={onSubmit}>
    <div class="flex flex-col gap-2">
        <Label for="external-id">
            <span>
                Import from <a
                    {href}
                    class="underline text-foreground inline-flex items-center gap-[0.25em] hover:text-primary"
                    target="_blank"
                >
                    {name}
                </a>
            </span>
        </Label>
        <div class="flex gap-2">
            <Input
                name="external-id"
                class="text-xs"
                {placeholder}
                disabled={isSubmitting}
            />
            <Button
                type="submit"
                class="p-0 ripple"
                disabled={isSubmitting}
            >
                {#if !showSpinner}
                    <ArrowRight
                        class="size-14 px-4 stroke-[2px] stroke-primary-foreground text-primary-foreground"
                    />
                {:else}
                    <Loader
                        class="size-14 p-4 stroke-primary-foreground text-primary-foreground"
                        showTrack={false}
                    />
                {/if}
            </Button>
        </div>
    </div>
</form>
