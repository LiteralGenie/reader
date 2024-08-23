<script lang="ts">
    import ArrowRight from '$lib/icons/arrow-right.svelte'
    import Button from '../ui/button/button.svelte'

    export let href: string
    export let disabled = false
</script>

<div class:disabled>
    <Button variant="link" {href}>
        <ArrowRight class="size-4 stroke-foreground stroke-1" />
    </Button>
</div>

<style lang="postcss">
    .disabled {
        @apply pointer-events-none opacity-50;
    }
</style>
