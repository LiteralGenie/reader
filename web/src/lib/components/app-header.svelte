<script lang="ts">
    import Bars_3 from '$lib/icons/bars-3.svelte'
    import ThemeToggle from './theme-toggle.svelte'
    import Button from './ui/button/button.svelte'
</script>

<div class="root w-full h-14 flex justify-between items-center pl-2">
    <Button
        variant="ghost"
        class="size-10 p-0 rounded-full mx-1 my-2"
    >
        <Bars_3 class="size-6 stroke-2" />
    </Button>

    <div class="pr-1 flex">
        <ThemeToggle
            variant="ghost"
            class="size-10 p-0 rounded-full mx-1 my-2"
        />
    </div>
</div>

<style lang="postcss">
    .root {
        background-color: var(--header);
    }
</style>
