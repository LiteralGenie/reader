<script lang="ts">
    import Label from '$lib/components/ui/label/label.svelte'
    import EditPageInput from './edit-page-input.svelte'

    export let series: string
    export let chapter: string

    const pages = [
        {
            filename: '001.png',
            action: null
        },
        {
            filename: '002.png',
            action: null
        },
        {
            filename: '003.png',
            action: {
                type: 'rename',
                filename: 'lmao.png'
            }
        },
        {
            filename: '004.png',
            action: null
        },
        {
            filename: '005.png',
            action: {
                type: 'delete'
            }
        },
        {
            filename: '006.png',
            action: null
        },
        {
            filename: '007.png',
            action: null
        },
        {
            filename: '008.png',
            action: null
        },
        {
            filename: '009.png',
            action: null
        }
    ] as const
</script>

<div class="h-full {$$restProps['class'] ?? ''}">
    <Label>Pages</Label>

    <div class="h-full pt-2 flex flex-col gap-2">
        {#each pages as pg}
            <EditPageInput page={pg} {series} {chapter} />
        {/each}
    </div>
</div>
