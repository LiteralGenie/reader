<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import ArrowUpTray from '$lib/icons/arrow-up-tray.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'
    import { createEventDispatcher } from 'svelte'

    let showImageOverlay = false
    let hasImage = true

    const dispatch = createEventDispatcher()
</script>

<div class="flex flex-col gap-1.5">
    <Label for="cover">Cover Image</Label>

    <div class="flex flex-col gap-2">
        <div class="relative">
            <button class="w-full flex justify-center">
                {#if hasImage}
                    <img
                        src="/api/cover/Knight%20Run/_reader_cover.png"
                        class="cover object-scale-down min-w-0 max-h-[40em] bg-[#050505] w-full"
                        on:mouseenter={() =>
                            (showImageOverlay = true)}
                        on:mouseleave={() =>
                            (showImageOverlay = false)}
                    />
                {:else}
                    <div
                        class="placeholder h-[20em] bg-[#303030] flex flex-col gap-2 items-center justify-center text-sm"
                        on:mouseenter={() =>
                            (showImageOverlay = true)}
                        on:mouseleave={() =>
                            (showImageOverlay = false)}
                    >
                        <ArrowUpTray class="size-12 stroke-2" />
                        <span class="font-bold">Tap to Upload</span>
                    </div>
                {/if}
            </button>

            <div
                class="overlay absolute top-0 bottom-0 left-0 right-0 p-0 flex items-center justify-center pointer-events-none"
                class:invisible={!showImageOverlay}
            >
                {#if hasImage}
                    <PencilSquare
                        class="size-16 stroke-white hidden"
                    />
                {/if}
            </div>
        </div>

        <div class="flex gap-2 justify-center">
            <Button
                on:click={() => dispatch('clear')}
                class="px-6 w-full flex gap-2 items-center"
                variant="secondary"
            >
                Clear
            </Button>
            <Button
                on:click={() => dispatch('download')}
                class="px-6 w-full"
                variant="secondary"
            >
                Download
            </Button>
        </div>
    </div>
</div>

<style lang="postcss">
    .overlay {
        background-color: rgba(0, 0, 0, 70%);
    }

    .placeholder {
        color: color-mix(
            in srgb,
            hsl(var(--muted-foreground)),
            hsl(var(--primary-foreground)) 70%
        );
    }
</style>
