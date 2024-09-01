<script lang="ts">
    import Label from '$lib/components/ui/label/label.svelte'
    import { getEditChapterContext } from '../../edit-chapter-dialog/editChapterContext'
    import EditPageInput from './edit-page-input.svelte'

    export let series: string
    export let chapter: string

    const { controls } = getEditChapterContext()
    $: pageControls = controls.children.existingPages.children
</script>

<div class={$$restProps['class'] ?? ''}>
    <Label>Pages</Label>

    <div class="pt-2 flex flex-col gap-2">
        {#each $pageControls as control}
            <EditPageInput {control} {series} {chapter} />
        {/each}
    </div>
</div>
