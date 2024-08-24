<script lang="ts">
    import { getReaderSettingsContext } from '$lib/contexts/readerSettingsContext'
    import BasicDialog from '../basic-dialog.svelte'
    import CheckboxItem from '../checkbox/checkbox-item.svelte'

    export let open = false

    const { settings, setSettings } = getReaderSettingsContext()
</script>

<BasicDialog
    {open}
    on:close
    class="min-w-80 h-max w-max px-6 pb-8 m-auto"
>
    <div class="pt-5 pb-8 flex items-center">
        <h1 class="text-xl font-bold">Reader Settings</h1>
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
