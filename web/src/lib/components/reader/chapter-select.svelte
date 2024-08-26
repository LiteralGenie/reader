<script lang="ts">
    import { goto } from '$app/navigation'
    import type { ChapterDto } from '$lib/api/dtos'
    import * as Select from '$lib/components/ui/select/index.js'
    import { euc } from '$lib/miscUtils'

    export let seriesId: string
    export let chapters: ChapterDto[]
    export let value: string

    $: selectedChapter = chapters.find((ch) => ch.filename === value)
    $: selected = {
        label: selectedChapter?.filename,
        value: selectedChapter
    }

    function onSelectedChange(val?: any) {
        const ch = val as ChapterDto | undefined
        if (!ch) {
            return
        }

        goto(`/series/${euc(seriesId)}/${euc(ch.filename)}`)
    }
</script>

<Select.Root
    onSelectedChange={(ev) => onSelectedChange(ev?.value)}
    {selected}
>
    <Select.Trigger class="h-full">
        <Select.Value placeholder={value} />
    </Select.Trigger>
    <Select.Content>
        <Select.Group>
            {#each chapters as ch}
                <Select.Item value={ch} label={ch.filename}>
                    {ch.filename}
                </Select.Item>
            {/each}
        </Select.Group>
    </Select.Content>
    <Select.Input name="favoriteFruit" />
</Select.Root>
