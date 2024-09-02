<script lang="ts">
    import type { ReadableParam } from '$lib/miscUtils'
    import { derived } from 'svelte/store'
    import type { EditChapterFormControls } from '../editChapterContext'
    import EditPageInput from './edit-page-input.svelte'

    export let control: ReadableParam<
        EditChapterFormControls['children']['existingPages']['children']
    >[number]
    export let series: string
    export let chapter: string

    $: ({ value: filenameValue } = control.children.filename)
    $: ({ value: actionValue, setValue: setAction } =
        control.children.action)

    $: inputState = derived(actionValue, (action) => {
        if (action === null) {
            return {
                type: 'default'
            } as const
        } else if (action.type === 'rename') {
            return {
                type: 'rename',
                newFilename: action.filename
            } as const
        } else {
            return {
                type: 'delete'
            } as const
        }
    })

    function onRename(update: string) {
        const ext = $filenameValue.split('.').slice(-1)[0]
        if (update && !update.endsWith(ext)) {
            update = update + '.' + ext
        }

        if (update && update !== $filenameValue) {
            setAction({
                type: 'rename',
                filename: update
            })
        } else {
            setAction(null)
        }
    }

    function onDelete() {
        setAction({
            type: 'delete'
        })
    }

    function onRestore() {
        setAction(null)
    }
</script>

<EditPageInput
    state={$inputState}
    filename={$filenameValue}
    src="/series/{series}/{chapter}/{$filenameValue}"
    on:rename={(ev) => onRename(ev.detail)}
    on:delete={onDelete}
    on:restore={onRestore}
/>
