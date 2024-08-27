<script lang="ts">
    import Bars_3 from '$lib/icons/bars-3.svelte'
    import ThemeToggle from './theme-toggle.svelte'
    import Button from './ui/button/button.svelte'
</script>

<div
    class="root w-full flex justify-between items-center pl-4 pr-2 py-1"
>
    <Button variant="ghost" class="size-10 p-0 rounded-full">
        <Bars_3 class="size-6 stroke-2" />
    </Button>

    <div class="flex">
        <ThemeToggle
            variant="ghost"
            class="size-10 p-0 rounded-full"
        />
    </div>
</div>

<style lang="postcss">
    .root {
        background-color: var(--header);
    }
</style>
