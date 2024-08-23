<script lang="ts">
    import { Button } from '$lib/components/ui/button/index.js'

    export let label: string
    export let href: string
    export let disabled = false
</script>

<div class="root flex items-center justify-center" class:disabled>
    <Button variant="link" {href}>{label}</Button>
</div>

<style lang="postcss">
    .disabled {
        @apply pointer-events-none;
    }

    .disabled :global(a) {
        @apply bg-gray-200;
    }

    /* .root :global(a) {
        @apply w-8 h-8 py-0;
    } */
</style>
