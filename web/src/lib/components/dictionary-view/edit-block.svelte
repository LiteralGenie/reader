<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    import Button from '../ui/button/button.svelte'
    import Textarea from '../ui/textarea/textarea.svelte'

    export let value: string

    let formEl: HTMLFormElement

    const dispatch = createEventDispatcher()

    function onSubmit() {
        let text =
            new FormData(formEl).get('block-text')?.toString() ?? ''
        text = text.replaceAll('\n', ' ')
        text = text.trim()

        if (text) {
            dispatch('submit', text)
        } else {
            dispatch('cancel')
        }
    }
</script>

<form
    bind:this={formEl}
    on:submit|preventDefault={onSubmit}
    class="flex flex-col gap-2"
>
    <Textarea name="block-text" {value} class="min-h-24 text-lg" />

    <div class="flex justify-end gap-2 items-center h-8">
        <Button
            variant="outline"
            class="hover:bg-muted hover:text-foreground h-full border-0"
            on:click={() => dispatch('cancel')}
        >
            Cancel
        </Button>

        <Button type="submit" class="h-full border-0">Submit</Button>
    </div>
</form>
