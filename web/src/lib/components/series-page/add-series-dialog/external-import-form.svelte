<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'

    import Label from '$lib/components/ui/label/label.svelte'
    import ArrowRight from '$lib/icons/arrow-right.svelte'

    export let label: string
    export let placeholder: string
</script>

<form on:submit>
    <div class="flex flex-col gap-2">
        <Label for="external-id">{label}</Label>
        <div class="flex gap-2">
            <Input name="external-id" class="text-xs" {placeholder} />
            <Button type="button" class="p-0 ripple">
                <ArrowRight
                    class="size-14 px-4 stroke-[2px] stroke-primary-foreground text-primary-foreground"
                />
            </Button>
        </div>
    </div>
</form>
