<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'

    import Label from '$lib/components/ui/label/label.svelte'

    export let label: string
    export let placeholder: string
    export let name: string
</script>

<div class="flex flex-col gap-1.5">
    <Label for={name}>{label}</Label>

    <div class="flex gap-1">
        <Input {name} required class="text-xs" {placeholder} />

        <Button class="flex gap-1">
            <span>Sync</span>
        </Button>
    </div>
</div>
