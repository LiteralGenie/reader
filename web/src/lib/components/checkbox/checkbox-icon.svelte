<script lang="ts">
    import CheckmarkIcon from '$lib/icons/checkmark-icon.svelte'

    export let checked: boolean
</script>

<div
    class:bg-primary={checked}
    class="h-[85%] w-[85%] box-content border border-primary rounded-sm flex justify-center items-center"
>
    {#if checked}
        <CheckmarkIcon
            class="h-full w-full p-[0.25em] stroke-2 stroke-primary-foreground text-primary-foreground"
        />
    {:else}{/if}
</div>

<style lang="postcss">
</style>
