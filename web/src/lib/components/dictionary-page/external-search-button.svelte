<script lang="ts">
    import ArrowTopRightOnSquare from '$lib/icons/arrow-top-right-on-square.svelte'
    import Button from '../ui/button/button.svelte'

    export let href: string
    export let label: string
    //
</script>

<Button
    class="bg-muted text-muted-foreground text-xs max-w-max py-2 px-3 self-end flex gap-1 h-auto items-start ripple"
    {href}
    referrerpolicy="no-referrer"
    target="_blank"
    variant="outline"
>
    <span> {label} </span>
    <ArrowTopRightOnSquare class="size-3.5" />
</Button>
