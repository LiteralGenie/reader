<script lang="ts">
    import ArrowUpTray from '$lib/icons/arrow-up-tray.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'

    let showImageOverlay = false
    let hasImage = false
</script>

<div class="relative flex flex-col justify-center">
    {#if hasImage}
        <img
            src="/api/cover/Knight%20Run/_reader_cover.png"
            class="cover object-scale-down min-w-0 max-h-[40em] bg-[#050505] cursor-pointer"
            on:mouseenter={() => (showImageOverlay = true)}
            on:mouseleave={() => (showImageOverlay = false)}
        />
    {:else}
        <div
            class="h-[20em] bg-[#303030] flex flex-col gap-2 items-center justify-center cursor-pointer text-muted-foreground text-sm"
            on:mouseenter={() => (showImageOverlay = true)}
            on:mouseleave={() => (showImageOverlay = false)}
        >
            <ArrowUpTray class="size-12 stroke-2" />
            <span class="font-bold">Tap to Upload</span>
        </div>
    {/if}

    <div
        class="overlay absolute top-0 bottom-0 left-0 right-0 p-0 flex items-center justify-center pointer-events-none"
        class:invisible={!showImageOverlay}
    >
        {#if hasImage}
            <PencilSquare class="size-16 stroke-white hidden" />
        {/if}
    </div>
</div>

<style lang="postcss">
    .overlay {
        background-color: rgba(0, 0, 0, 80%);
    }
</style>
