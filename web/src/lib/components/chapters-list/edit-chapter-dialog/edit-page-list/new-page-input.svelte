<script lang="ts">
    import type { ReadableParam } from '$lib/miscUtils'
    import {
        getEditChapterContext,
        type EditChapterFormControls
    } from '../editChapterContext'
    import EditPageInput from './edit-page-input.svelte'

    export let control: ReadableParam<
        EditChapterFormControls['children']['newPages']['children']
    >[number]
    export let disabled: boolean

    const { errors } = getEditChapterContext()

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

    $: isError = !!$errors.duplicates?.includes(
        inputState.newFilename || $file.name
    )

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
    {isError}
    {disabled}
    on:rename={(ev) => onRename(ev.detail)}
    on:delete
/>
