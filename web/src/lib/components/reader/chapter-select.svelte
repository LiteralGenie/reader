<script lang="ts">
    import { goto } from '$app/navigation'
    import type { ChapterDto } from '$lib/api/dtos'
    import * as Select from '$lib/components/ui/select/index.js'
    import { euc } from '$lib/miscUtils'

    export let seriesId: string
    export let chapters: ChapterDto[]
    export let value: string

    $: chaptersSorted = chapters.toReversed()
    $: selectedChapter = chaptersSorted.find(
        (ch) => ch.filename === value
    )
    $: selected = {
        label: selectedChapter?.filename,
        value: selectedChapter
    }

    $: refs = [] as any[]

    function onSelectedChange(val?: any) {
        const ch = val as ChapterDto | undefined
        if (!ch) {
            return
        }

        goto(`/series/${euc(seriesId)}/${euc(ch.filename)}`)
    }

    function onOpenChange(isOpen: boolean) {
        if (!isOpen) {
            return
        }

        // Scroll to selected chapter
        // Open event fires before refs are updated so need to delay it
        setTimeout(() => {
            const idxSelected = chaptersSorted.findIndex(
                (ch) => ch.filename === value
            )
            if (idxSelected < 0) {
                return
            }

            refs[idxSelected]?.scrollIntoView({ block: 'center' })
        }, 10)
    }
</script>

<Select.Root
    onSelectedChange={(ev) => onSelectedChange(ev?.value)}
    onOpenChange={(ev) => onOpenChange(ev)}
    {selected}
>
    <Select.Trigger class="h-full">
        <Select.Value placeholder={value} />
    </Select.Trigger>
    <Select.Content class="max-h-[50vh] overflow-auto">
        <Select.Group>
            {#each chaptersSorted as ch, idx}
                <Select.Item value={ch} label={ch.filename}>
                    <span bind:this={refs[idx]}>{ch.filename}</span>
                </Select.Item>
            {/each}
        </Select.Group>
    </Select.Content>
    <Select.Input name="favoriteFruit" />
</Select.Root>
