<script lang="ts">
    import ThemeToggle from '../theme-toggle.svelte'
</script>

<div class="root w-full h-14 flex justify-between items-center">
    <div></div>

    <div class="pr-2 flex">
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
