<script lang="ts">
    import ArrowLeft from '$lib/icons/arrow-left.svelte'
    import Button from '../ui/button/button.svelte'

    export let href: string
    export let disabled = false
</script>

<div class:disabled>
    <Button variant="link" {href}>
        <ArrowLeft class="size-4 stroke-black stroke-1" />
    </Button>
</div>

<style lang="postcss">
    .disabled {
        @apply pointer-events-none opacity-50;
    }
</style>
