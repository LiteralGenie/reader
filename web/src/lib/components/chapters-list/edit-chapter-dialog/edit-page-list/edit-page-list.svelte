<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import Plus from '$lib/icons/plus.svelte'
    import { getUuidWithFallback } from '$lib/miscUtils'
    import { alphabetical } from 'radash'
    import { derived, get } from 'svelte/store'
    import { getEditChapterContext } from '../../edit-chapter-dialog/editChapterContext'
    import EditPageInput from './existing-page-input.svelte'
    import NewPageInput from './new-page-input.svelte'

    export let series: string
    export let chapter: string
    export let disabled: boolean

    let inputEl: HTMLInputElement

    const { controls, errors } = getEditChapterContext()

    $: existingPages = controls.children.existingPages.children
    $: newPages = controls.children.newPages.children

    $: hasDupes = 'duplicates' in $errors

    $: inputComponents = derived(
        [existingPages, newPages],
        ([existingPgs, newPgs]) => {
            const comps: any[] = []

            for (let control of existingPgs) {
                const val = get(control.value)

                comps.push({
                    component: EditPageInput,
                    props: {
                        control,
                        series,
                        chapter
                    },
                    forKey: `exist_${val.filename}`,
                    sortKey: (val.action?.type === 'rename'
                        ? val.action.filename
                        : val.filename
                    ).toLowerCase()
                })
            }

            for (let control of newPgs) {
                const val = get(control.value)

                comps.push({
                    component: NewPageInput,
                    props: {
                        control
                    },
                    forKey: `new_${val.id}`,
                    sortKey: (
                        val.newFilename || val.file.name
                    ).toLowerCase(),
                    onDelete: () => onNewPageDelete(val.id)
                })
            }

            return alphabetical(comps, (c) => c.sortKey)
        }
    )

    function onPageUpload() {
        const files = inputEl.files
        if (!files?.length) {
            return
        }

        const update = [...get(controls.children.newPages.value)]
        for (let file of files) {
            update.push({
                id: getUuidWithFallback(),
                file,
                newFilename: null
            })
        }

        controls.children.newPages.setValue(update)
    }

    function onNewPageDelete(id: string) {
        const curr = get(controls.children.newPages.value)
        const update = curr.filter((pg) => pg.id !== id)
        if (curr.length === update.length) {
            return
        }

        controls.children.newPages.setValue(update)
    }
</script>

<div class={$$restProps['class'] ?? ''}>
    <div
        class="flex justify-between items-center"
        class:text-red-500={hasDupes}
    >
        <div class="flex flex-col gap-0 leading-none">
            <Label class="text-base">Pages</Label>
            {#if hasDupes}
                <p class="text-sm">File names must be unique.</p>
            {/if}
        </div>

        <Button
            on:click={() => inputEl.click()}
            variant="secondary"
            class="p-0 w-16 h-7 py-2 mr-2 flex gap-0.5"
            {disabled}
        >
            <Plus class="h-3 stroke-[4px]" />

            <span class="text-xs font-bold uppercase">Add</span>

            <input
                on:change={onPageUpload}
                bind:this={inputEl}
                hidden
                type="file"
                accept="image/*"
                multiple
            />
        </Button>
    </div>

    <div class="pt-2 flex flex-col gap-2">
        {#each $inputComponents as d (d.forKey)}
            <svelte:component
                this={d.component}
                {...d.props}
                on:delete={d.onDelete}
                {disabled}
            />
        {/each}
    </div>
</div>
