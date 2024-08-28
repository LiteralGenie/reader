<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import ArrowRight from '$lib/icons/arrow-right.svelte'
    import { createEventDispatcher } from 'svelte'

    export let name: string
    export let href: string
    export let placeholder: string

    const dispatch = createEventDispatcher()

    function onSubmit(ev: SubmitEvent) {
        const data = new FormData(ev.target as HTMLFormElement)
        dispatch('submit', data.get('external-id')!)
    }
</script>

<form on:submit={onSubmit}>
    <div class="flex flex-col gap-2">
        <Label for="external-id">
            <span>Import from <a {href}>{name}</a></span>
        </Label>
        <div class="flex gap-2">
            <Input name="external-id" class="text-xs" {placeholder} />
            <Button type="submit" class="p-0 ripple">
                <ArrowRight
                    class="size-14 px-4 stroke-[2px] stroke-primary-foreground text-primary-foreground"
                />
            </Button>
        </div>
    </div>
</form>
