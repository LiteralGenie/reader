<script lang="ts">
    import Bars_2 from '$lib/icons/bars-2.svelte'
    import { clamp } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'

    export let maxHeightPercent = 85
    export let minHeightPercent = 10
    export let storageKey: string

    let heightPercent =
        parseInt(localStorage?.getItem(storageKey) ?? '') || 40
    let isDragging = false
    let resizeEl: HTMLDivElement

    $: {
        localStorage?.setItem(storageKey, String(heightPercent))
    }

    const dispatch = createEventDispatcher()

    function onDragStart(ev: DragEvent | MouseEvent | TouchEvent) {
        isDragging = true
        dispatch('resizestart')
    }

    function onDrag(ev: DragEvent | MouseEvent | TouchEvent) {
        if (!isDragging) {
            return
        }

        let clientY =
            'clientY' in ev ? ev.clientY : ev.touches[0].clientY
        if (clientY === 0) {
            // Final drag event after mouse release tends to be wrong on Chrome
            // https://stackoverflow.com/questions/40368047/why-do-my-coordinates-pagex-pagey-change-at-end-of-drag
            return
        }

        heightPercent =
            100 -
            clamp(
                // Small offset so that mouse remains centered on resize bar instead of at edge
                (100 * (clientY - resizeEl.clientHeight / 2)) /
                    window.innerHeight,
                minHeightPercent,
                maxHeightPercent
            )
    }

    function onDragEnd() {
        isDragging = false
        dispatch('resizeend')
    }
</script>

<svelte:document on:mousemove={onDrag} on:touchmove={onDrag} />

<div
    style="height: {heightPercent}%"
    class:dragging={isDragging}
    class="relative flex flex-col justify-center h-full w-full z-20"
>
    <div
        draggable="false"
        bind:this={resizeEl}
        on:drag={onDrag}
        on:dragstart={onDragStart}
        on:dragend={onDragEnd}
        on:mousemove={onDrag}
        on:mousedown={onDragStart}
        on:mouseup={onDragEnd}
        on:touchstart|preventDefault={onDragStart}
        on:touchend|preventDefault={onDragEnd}
        on:touchcancel={onDragEnd}
        class="w-full flex justify-center cursor-ns-resize bg-background"
    >
        <Bars_2 class="h-6 pointer-events-none" />
    </div>

    <div
        class:overflow-hidden={isDragging}
        class="h-full flex-grow min-h-0 overflow-auto"
    >
        <slot />
    </div>
</div>

{#if isDragging}
    <div style="height: {heightPercent}%" class="w-full"></div>
{/if}

<style lang="postcss">
    .dragging {
        position: absolute;
        bottom: 0;
    }
</style>
