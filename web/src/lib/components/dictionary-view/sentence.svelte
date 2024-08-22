<script lang="ts">
    import type { MtlDto } from '$lib/api/mtl'
    import { newPromiseStore } from '$lib/promiseStore'

    export let text: string
    export let mtl: Promise<MtlDto | null>

    $: mtlText = newPromiseStore(mtl, null)
</script>

<div>
    <span>{text}</span>

    {#if mtlText}
        <span class="italic">{mtlText}</span>
    {/if}
</div>
