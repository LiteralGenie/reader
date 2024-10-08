<script lang="ts">
    import { cn } from '$lib/utils.js'
    import { Dialog as SheetPrimitive } from 'bits-ui'
    import X from 'lucide-svelte/icons/x'
    import { fly } from 'svelte/transition'
    import {
        SheetOverlay,
        SheetPortal,
        type Side,
        sheetTransitions,
        sheetVariants
    } from './index.js'

    type $$Props = SheetPrimitive.ContentProps & {
        side?: Side
        showCloseIcon?: boolean
        inTransitionExtras?: Partial<
            SheetPrimitive.ContentProps['inTransitionConfig']
        >
        outTransitionExtras?: Partial<
            SheetPrimitive.ContentProps['outTransitionConfig']
        >
    }

    let className: $$Props['class'] = undefined
    export let side: $$Props['side'] = 'right'
    export { className as class }
    export let inTransition: $$Props['inTransition'] = fly
    export let inTransitionConfig: $$Props['inTransitionConfig'] =
        sheetTransitions[side ?? 'right'].in
    export let outTransition: $$Props['outTransition'] = fly
    export let outTransitionConfig: $$Props['outTransitionConfig'] =
        sheetTransitions[side ?? 'right'].out

    export let showCloseIcon = false

    export let inTransitionExtras: Partial<
        $$Props['inTransitionConfig']
    > = {}
    export let outTransitionExtras: Partial<
        $$Props['outTransitionConfig']
    > = {}
</script>

<SheetPortal>
    <SheetOverlay />
    <SheetPrimitive.Content
        {inTransition}
        inTransitionConfig={{
            ...inTransitionConfig,
            ...inTransitionExtras
        }}
        {outTransition}
        outTransitionConfig={{
            ...outTransitionConfig,
            ...outTransitionExtras
        }}
        class={cn(sheetVariants({ side }), className)}
        {...$$restProps}
    >
        <slot />

        <SheetPrimitive.Close
            class="ring-offset-background focus:ring-ring data-[state=open]:bg-secondary absolute right-4 top-4 rounded-sm opacity-70 transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:pointer-events-none
                {showCloseIcon ? '' : 'hidden'}"
        >
            <X class="h-4 w-4" />
            <span class="sr-only">Close</span>
        </SheetPrimitive.Close>
    </SheetPrimitive.Content>
</SheetPortal>
