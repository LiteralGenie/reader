<script lang="ts">
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'

    import Loader from '$lib/components/loader.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import type { FormControl } from '$lib/form/types'
    import { syncStringInput } from '$lib/form/utils'
    import type { ImportedSeries } from '$lib/import-handlers'
    import type { Unsubscribe } from '$lib/miscUtils'
    import { get, writable } from 'svelte/store'
    import { getEditSeriesContext } from './editSeriesContext'

    export let source: string
    export let placeholder: string
    export let name: string
    export let href: string
    export let importFn: (id: string) => Promise<ImportedSeries>
    export let control: FormControl<string>
    export let disabled = false
    export let isSyncing = false

    let inputEl: Input
    const subSink = writable<Unsubscribe[]>([])
    $: syncStringInput(inputEl, control, subSink)

    const { controls } = getEditSeriesContext()

    async function onSync() {
        isSyncing = true

        try {
            const id = get(control.value)
            if (!id) {
                return
            }

            const data = await importFn(id)

            controls.children.name.setValue(data.name)

            if (data.coverBytes) {
                const file = new File([data.coverBytes], 'cover')
                controls.children.cover.setValue(file)
            }
        } catch (e) {
            alert(String(e))
        } finally {
            isSyncing = false
        }
    }
</script>

<div class="flex flex-col gap-1.5">
    <Label for={name}>
        <span> Import from </span>
        <a
            {href}
            class="underline text-foreground inline-flex items-center gap-[0.25em] hover:text-primary cursor-pointer"
            target="_blank"
        >
            {source}
        </a>
    </Label>

    <div class="flex gap-1">
        <Input
            bind:this={inputEl}
            {name}
            {placeholder}
            class="text-xs"
        />

        <Button
            on:click={onSync}
            {disabled}
            class="flex gap-1 font-bold w-20 h-10"
        >
            {#if !isSyncing}
                Sync
            {:else}
                <Loader
                    class="h-full w-full stroke-primary-foreground text-primary-foreground"
                    showTrack={false}
                />
            {/if}
        </Button>
    </div>
</div>
