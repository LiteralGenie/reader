<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'

    import Label from '$lib/components/ui/label/label.svelte'

    export let source: string
    export let placeholder: string
    export let name: string
    export let href: string
</script>

<div class="flex flex-col gap-1.5">
    <Label for={name}>
        <span> Import from </span>
        <a
            {href}
            class="underline text-foreground inline-flex items-center gap-[0.25em] hover:text-primary cursor-pointer"
            target="_blank"
        >
            {source}
        </a>
    </Label>

    <div class="flex gap-1">
        <Input {name} required class="text-xs" {placeholder} />

        <Button class="flex gap-1 font-bold">Sync</Button>
    </div>
</div>
