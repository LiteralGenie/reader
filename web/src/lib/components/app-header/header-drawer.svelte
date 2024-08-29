<script lang="ts">
    import * as Sheet from '$lib/components/ui/sheet'
</script>

<Sheet.Root>
    <Sheet.Trigger>
        <slot name="trigger" />
    </Sheet.Trigger>
    <Sheet.Content
        inTransitionExtras={{ duration: 200 }}
        outTransitionExtras={{ duration: 200 }}
        side="left"
        showCloseIcon={false}
        class="p-0"
    >
        <slot />
    </Sheet.Content>
</Sheet.Root>
