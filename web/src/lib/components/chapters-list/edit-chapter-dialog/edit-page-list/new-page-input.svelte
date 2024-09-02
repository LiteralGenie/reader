<script lang="ts">
    import type { ReadableParam } from '$lib/miscUtils'
    import type { EditChapterFormControls } from '../editChapterContext'
    import EditPageInput from './edit-page-input.svelte'

    export let control: ReadableParam<
        EditChapterFormControls['children']['newPages']['children']
    >[number]

    $: ({ file: fileControl, newFilename: newFilenameControl } =
        control.children)
    $: ({ value: file } = fileControl)
    $: ({ value: newFilename, setValue: setNewFilename } =
        newFilenameControl)

    $: inputState =
        $newFilename === null
            ? ({ type: 'default' } as const)
            : ({ type: 'rename', newFilename: $newFilename } as const)

    $: src = URL.createObjectURL($file)

    function onRename(update: string) {
        const ext = $file.name.split('.').slice(-1)[0].trim()
        if (update && ext && !update.endsWith(ext)) {
            update = update + '.' + ext
        }

        if (update && update !== $file.name.trim()) {
            setNewFilename(update)
        } else {
            setNewFilename(null)
        }
    }
</script>

<EditPageInput
    state={inputState}
    filename={$file.name.trim()}
    {src}
    isNew={true}
    on:rename={(ev) => onRename(ev.detail)}
    on:delete
/>
