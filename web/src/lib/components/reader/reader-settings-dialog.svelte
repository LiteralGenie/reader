<script lang="ts">
    import { getReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import XIcon from '$lib/icons/x-icon.svelte'
    import { createEventDispatcher } from 'svelte'
    import BasicDialog from '../basic-dialog/basic-dialog.svelte'
    import CheckboxItem from '../checkbox/checkbox-item.svelte'
    import Button from '../ui/button/button.svelte'

    export let open = false

    const { settings, setSettings } = getReaderSettingsContext()

    const dispatch = createEventDispatcher()
</script>

<BasicDialog
    {open}
    on:close
    class="min-w-80 h-max w-max px-6 pb-8 m-auto"
>
    <div class="pt-5 pb-8 flex items-center justify-between">
        <h1 class="text-xl font-bold">Reader Settings</h1>

        <Button
            variant="ghost"
            class="absolute top-3 right-3 rounded-full p-0 h-max w-max hover:bg-background"
            on:click={() => dispatch('close')}
        >
            <XIcon class="size-12 p-2" />
        </Button>
    </div>

    <CheckboxItem
        on:change={(ev) =>
            setSettings({ ...$settings, debugBboxs: ev.detail })}
        id="bbox"
        value={$settings.debugBboxs}
        label="Debug bounding boxes"
    />
</BasicDialog>

<style lang="postcss">
</style>
